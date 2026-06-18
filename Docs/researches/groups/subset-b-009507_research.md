# subset-b-009507 research

Grouped research for the syzkaller `prog` package files assigned to `subset-b-009507`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/analysis.go -->
# sources/test-tools/syzkaller/prog/analysis.go

Purpose: implements conservative program analysis, argument traversal, feature detection, fallback coverage signal construction, compressed-asset enumeration, and a top-level `ContainsAny` query.

Important APIs/types/functions: `state` tracks target, choice table, corpus, observed filenames/strings/resources, and memory/VMA allocators. `analyze`, `newState`, `(*state).analyze`, and `analyzeImpl` walk calls and update allocation/resource/string/file state. `ArgCtx`, `ForeachArg`, `ForeachSubArg`, and `foreachArgImpl` are central traversal APIs used across checksum, encoding, hints, minimization, and conditional-field logic. `RequiredFeatures`, `CallInfo`, `FallbackSignal`, `DecodeFallbackSignal`, `ForEachAsset`, and `ContainsAny` are package-level program introspection entry points.

Control flow and state: `analyze` processes calls before a requested stop call with resource recording disabled once the stop call is reached. `analyzeImpl` records pointer heap/VMA allocations, output resources, non-output string buffers, and local non-escaping filenames. Traversal preserves and restores `ArgCtx` around recursive descent, carrying parent slices, field metadata, base pointer, offset, and optional parent stack. `FallbackSignal` walks executed calls, emits errno/blocked signals, collects successful resource producers, and adds constructor/argument-flag signals until a syscall with `BreaksReturns`.

Dependencies and integration: depends on `pkg/image` for decompressing `BufferCompressed` data and on `any.go` through `Target.CallContainsAny`. The traversal primitives are integration points for most other files in this subset. Fallback signal values must remain compatible with signal consumers and the `fallbackCallMask` bit layout.

Risks: traversal offset handling is subtle for overlays, varlen groups, unions, and pointer bases. `FallbackSignal` intentionally truncates errno space and call IDs; call ID overflow panics. `ForEachAsset` uses `image.MustDecompress`, so malformed compressed data would fail hard if earlier deserialization validation missed it.

Test signals: coverage is indirect through serialization, checksum, hints, minimization, images, and conditional-field tests. `images_test.go` directly verifies `ForEachAsset`; `prog_test.go` outside this item covers fallback signal behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/analysis.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/any.go -->
# sources/test-tools/syzkaller/prog/any.go

Purpose: manages syzkaller's generated `ANY` pointer representation and squashes complex pointer pointees into an `ANYPTRS` array of byte blobs and resource tokens.

Important APIs/types/functions: `anyTypes` caches builtin `ANYPTRS` component types. `initAnyTypes`, `getAnyPtrType`, `isAnyPtr`, `isAnyRes`, `CallContainsAny`, and `ArgContainsAny` identify any pointers/resources. `complexPtr`, `Prog.complexPtrs`, and `Target.isComplexPtr` classify generated complex pointers. `squashPtr`, `squashPtrImpl`, `squashConst`, `squashResult`, `squashGroup`, `squashedValue`, and `ensureDataElem` implement conversion to `ANYBLOB`/`ANYRES*` union elements.

Control flow and state: target initialization locates builtin `ANYPTRS` in `Target.Types` and stores exact type references for later identity comparisons. Squashing mutates a `PointerArg` in place by replacing its type reference and pointee, while preserving total pointee size. Constants become little-endian/native bytes or fixed-width decimal/hex/octal strings; big-endian constants are byte-swapped before storage. Result args are retyped to the matching `ANYRES` resource union option and keep their resource relationship.

Dependencies and integration: relies on builtin compiler-generated type layout, `ForeachArg`/`ForeachSubArg` from `analysis.go`, arg constructors, endian helpers, and resource use tracking. The text parser/serializer understands `ANY=` and the executor writer serializes the squashed result like ordinary pointer data.

Risks: panics protect unsupported bitfields, overlay structs, bad pointer sizes, and size drift. Incorrect builtin ordering would corrupt all `ANY` interpretation. Squashing mutates result arg type refs, so it must preserve resource-use invariants.

Test signals: `any_test.go` checks static/runtime complex-pointer detection and exact squashed serialization, including idempotent double squash and non-squashable inout/overlay/filename cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/any.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/any_test.go -->
# sources/test-tools/syzkaller/prog/any_test.go

Purpose: validates `ANY` pointer classification and squashing behavior.

Important APIs/types/functions: `TestIsComplexPtr` enumerates all statically squashable pointer element types and compares them with randomly generated complex pointers. `TestSquash` deserializes hand-written programs, invokes `Target.isComplexPtr`, `ArgContainsAny`, and `squashPtr`, then compares serialized output.

Control flow and state: random target-wide generation is skipped in short/race-heavy modes to control runtime. `TestSquash` mutates the same pointer twice to prove squashing is idempotent and that the pointer remains size-stable after conversion.

Dependencies and integration: uses target test helpers from `export_test.go`, generated test descriptions, `Deserialize`, `Serialize`, and the `any.go` implementation. The tests exercise integration with parser support for `ANY=` and serializer output.

Risks: `TestIsComplexPtr` is probabilistic and only requires 90% runtime generation coverage, so rare generator coverage regressions can be noisy. Exact serialized strings make `TestSquash` sensitive to intentional format changes.

Test signals: strong targeted checks for blob/resource packing, endian byte order, padding, unsupported overlays, inout pointers, filename unions, and duplicate squashing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/any_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/big_endian.go -->
# sources/test-tools/syzkaller/prog/big_endian.go

Purpose: provides the package-level host byte order for big-endian builds.

Important APIs/types/functions: under build tag `s390x`, declares `var HostEndian = binary.BigEndian`.

Control flow and state: no runtime control flow; build constraints select this file at compile time. `HostEndian` is global immutable-by-convention state used by code that needs host-native byte order.

Dependencies and integration: imports `encoding/binary`; paired with `little_endian.go` so exactly one host-endian definition exists for supported architectures.

Risks: missing build tags for a new big-endian architecture would omit or misselect `HostEndian`. Any code assuming little-endian host behavior must use target-specific formats instead.

Test signals: no direct tests in this subset; endian behavior is indirectly exercised by executor serialization tests that inspect `FormatBigEndian` metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/big_endian.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/checksum.go -->
# sources/test-tools/syzkaller/prog/checksum.go

Purpose: derives runtime checksum calculation descriptors for syscall arguments, including Internet checksums and IPv4/IPv6 pseudo-header checksums.

Important APIs/types/functions: `CsumChunkKind`, `CsumInfo`, and `CsumChunk` model checksum inputs. `calcChecksumsCall` is the main entry point. `findCsummedArg`, `composePseudoCsumIPv4`, `composePseudoCsumIPv6`, `extractHeaderParams`, and `getFieldByName` locate checksum-covered regions and construct chunk lists.

Control flow and state: `calcChecksumsCall` first collects checksum fields with `ForeachArg`, builds a child-to-parent map for structs, and returns nil maps when no checksum is present. Inet checksums reference the configured parent or named ancestor. Pseudo checksums scan for IPv4/IPv6 header structs, extract `src_ip`/`dst_ip`, add protocol and packet length constants in network byte order, and record all args used by checksum instructions.

Dependencies and integration: used by `encodingexec.go` before copyin/checksum emission. Depends on `CsumType`, `CsumKind`, struct template names, swap helpers, and traversal from `analysis.go`.

Risks: missing headers, missing parent fields, bad `src_ip`/`dst_ip` sizes, and unknown checksum kinds panic. Named-buffer lookup currently compares type names and has a TODO for template argument names.

Test signals: `checksum_test.go` randomly generates and mutates programs, calling exported `CalcChecksumsCall` on every call. `encodingexec_test.go` includes exact executor-byte expectations for nested IPv4/TCP checksum instructions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/checksum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/checksum_test.go -->
# sources/test-tools/syzkaller/prog/checksum_test.go

Purpose: stress-tests checksum descriptor generation on generated and mutated Linux/amd64 programs.

Important APIs/types/functions: `TestChecksumCalcRandom` uses `InitTest`, `DefaultChoiceTable`, `Target.Generate`, `Prog.Mutate`, and exported `CalcChecksumsCall`.

Control flow and state: for each randomized iteration it generates a 10-call program, calculates checksum info for every call, mutates the program, and recalculates checksum info. It does not assert exact descriptors; it relies on panics/failures to catch invalid traversal or descriptor assumptions.

Dependencies and integration: package is `prog_test`, importing `prog` through dot import and `_ "github.com/google/syzkaller/sys"` to register syscall descriptions. Exported test aliases are provided by `export_test.go`.

Risks: random stress can miss specific pseudo-header edge cases, while failures may depend on target descriptions changing. It is a panic-safety test rather than a golden-output test.

Test signals: broad randomized coverage for checksum field discovery across generation and mutation; exact checksum wire-format coverage lives in `encodingexec_test.go`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/checksum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/clone.go -->
# sources/test-tools/syzkaller/prog/clone.go

Purpose: deep-clones programs, calls, and arguments while preserving resource reference topology and use maps.

Important APIs/types/functions: `Prog.Clone`, `cloneWithMap`, `cloneCalls`, `cloneCall`, `CloneArg`, and internal `clone`.

Control flow and state: `Prog.Clone` creates a fresh `newargs` map so cloned `ResultArg` producers can be substituted into cloned consumer `Res` pointers. `clone` copies scalar arg structs, clones data byte slices, recurses through pointer/group/union contents, rebuilds `uses` for referenced resources, clears producer `uses` to be rebuilt, and records old-to-new result mappings.

Dependencies and integration: used heavily by mutation, minimization, collide transformations, and hints. Relies on `slices.Clone`, arg concrete types, `debugValidate`, and resource `uses` invariants.

Risks: unsafe programs intentionally panic on clone to avoid mutating VM-check/corpus-unsafe programs. Passing `nil` as `newargs` to clone detached calls/args keeps `Res` pointing at original producers, which is intentional for some collide duplication but dangerous if used incorrectly.

Test signals: clone behavior is indirectly covered by mutation, minimization, hints, collide, and serialization round-trip tests that mutate cloned programs and expect stable originals/resource references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/clone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/collide.go -->
# sources/test-tools/syzkaller/prog/collide.go

Purpose: implements program transformations intended to trigger race conditions by assigning async/rerun properties and duplicating calls.

Important APIs/types/functions: `maxAsyncPerProg`, `AssignRandomAsync`, `AssignRandomRerun`, `DoubleExecCollide`, and `DupCallCollide`.

Control flow and state: `AssignRandomAsync` clones the program and walks calls backward, avoiding async producers whose resources are needed too soon, never marking the last call async, and capping async calls at 24. `AssignRandomRerun` assigns rerun counts to selected adjacent async pairs. `DoubleExecCollide` appends a clone of all calls and marks the duplicate prefix async. `DupCallCollide` randomly selects up to one third of calls, inserts async duplicates before originals, and respects `MaxCalls`.

Dependencies and integration: depends on `Clone`, `cloneCalls`, `cloneCall`, `ForeachArg`, resource direction semantics, `CallProps`, and executor thread limits described in comments.

Risks: async assignment is a heuristic and cannot guarantee producer completion. Duplicating with `cloneCalls(..., nil)` intentionally leaves duplicate resource references tied to first-half producers for double execution; changing this would alter collide semantics. Transformations must not exceed `MaxCalls` or executor async capacity.

Test signals: `collide_test.go` verifies resource-safe async placement, exact duplicate serialization with properties stripped, async insertion variants, and expected failure for too-small/too-large inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/collide.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/collide_test.go -->
# sources/test-tools/syzkaller/prog/collide_test.go

Purpose: verifies collide/race-oriented program transformations.

Important APIs/types/functions: `TestAssignRandomAsync`, `TestDoubleExecCollide`, and `TestDupCallCollide`.

Control flow and state: tests deserialize small Linux programs, repeatedly apply random transformations, and assert structural invariants. `TestAssignRandomAsync` ensures resource-producing calls are not made async when immediate consumers would break. `TestDoubleExecCollide` strips call props to compare duplicated call order. `TestDupCallCollide` samples up to 100 iterations and requires expected serialized variants to appear.

Dependencies and integration: uses `GetTarget`, `Deserialize`, `Serialize`, `Clone`, `CallProps`, random sources from `initTest`, and `testify/assert`.

Risks: random variant detection can be sensitive to iteration count and RNG changes. Exact serialization comparisons can fail on harmless formatter changes.

Test signals: covers async safety, clone/reference behavior for duplicated calls, `CallProps.Async` placement, and transformation error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/collide_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/decodeexec.go -->
# sources/test-tools/syzkaller/prog/decodeexec.go

Purpose: decodes the irreversible executor binary format into inspectable `ExecProg` structures for tests, diagnostics, and size accounting.

Important APIs/types/functions: `ExecProg`, `ExecCall`, `ExecCopyin`, `ExecCopyout`, `ExecArgConst`, `ExecArgResult`, `ExecArgData`, `ExecArgCsum`, `ExecCsumChunk`, `ExecCallCount`, `Target.DeserializeExec`, and `execDecoder` methods `parse`, `readCallProps`, `readArg`, `read`, `readBlob`, `commitCall`, `addStat`.

Control flow and state: parsing reads varints from `data`, beginning with call count, then processes copyin/copyout/set-props/syscall/EOF instructions. `commitCall` finalizes pending calls before instruction boundaries, updates `numVars`, and resets decoder call state. Result args extend `vars` with default values. Stats are accumulated hierarchically by slash-separated path prefixes.

Dependencies and integration: mirrors constants and wire layout from `encodingexec.go`, adds `target.DataOffset` back to physical addresses, and uses target syscall tables to resolve call IDs.

Risks: decoder must stay byte-for-byte compatible with serializer changes. It rejects bad syscall IDs, unsupported checksum kinds, bad top-level arg kinds, varint/blob overflow, and mismatched call counts. It decodes for inspection, not for reconstructing a normal `Prog`.

Test signals: `encodingexec_test.go` round-trips serialized executor buffers through `DeserializeExec`, compares selected decoded structs, validates `ExecCallCount`, and records stats in random tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/decodeexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encoding.go -->
# sources/test-tools/syzkaller/prog/encoding.go

Purpose: implements human-readable program serialization/deserialization, data literal encoding, comment handling, `AUTO` fixups, conditional fixups, and conservative call-set parsing.

Important APIs/types/functions: `Prog.String`, `Serialize`, `SerializeVerbose`, `serializer.call/arg`, concrete `serialize` methods, `DeserializeMode`, `Target.Deserialize`, parser methods `parseProg`, `parseCallProps`, `parseArg*`, `deserializeData`, `fixupAutos`, `fixupConditionals`, `CallSet`, and `highlightError`.

Control flow and state: serialization assigns result variable IDs lazily, omits defaults unless verbose, handles `ANY=`, compressed-image elision, call props, and readable versus hex data. Deserialization scans line by line, attaches comments, parses calls/args/properties, repairs malformed input in non-strict mode, validates with transient conditional fields ignored, patches conditionals/AUTO values, and sanitizes unless unsafe. Parser state includes strict/unsafe flags, variable bindings, pending `AUTO` args, current line, and first error.

Dependencies and integration: central integration point for target descriptions, arg constructors, `analysis.go` allocation state, `expr.go` conditionals, image compression, sanitization, executor serialization tests, and almost all package tests.

Risks: parser repair paths (`eatExcessive`, default args, non-strict errors) are compatibility-sensitive. `AUTO` fixups must coordinate sizes, memory allocation, constants, and checksums. Compressed data validation and unsafe modes affect security/safety boundaries. Serializer default elision must not change semantic union choices.

Test signals: `encoding_test.go` extensively covers data escaping, call-set parsing, strict/non-strict repair, `AUTO`, comments, call props, image skipping, random serialize/deserialize equivalence, and executor-byte equivalence after round trip.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encoding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encoding_test.go -->
# sources/test-tools/syzkaller/prog/encoding_test.go

Purpose: validates text serialization/deserialization, repair behavior, data encoding, comments, call props, image skipping, and text-to-executor semantic stability.

Important APIs/types/functions: `TestSerializeData`, `TestCallSet`, `TestCallSetRandom`, `TestDeserialize`, `TestSerializeDeserialize`, `TestDeserializeDataMmapProg`, `TestSerializeDeserializeRandom`, `testSerializeDeserialize`, `TestSerializeCallProps`, `TestDeserializeComments`, `TestHasNext`, and `TestDeserializeSkipImage`.

Control flow and state: table-driven tests feed malformed and valid programs through strict/non-strict modes and compare expected serialized output or expected errors. Random tests generate programs, serialize to text, deserialize, and require identical executor buffers. Failure minimization uses `Minimize` to shrink random counterexamples.

Dependencies and integration: uses target test helpers, `DeserializeTest` helpers from surrounding package tests, `SerializeForExec`, `DeserializeExec`, `Minimize`, `pkg/image`, and `testify`.

Risks: exact strings couple tests to serializer formatting. Random round-trip checks can be expensive and skip very large arg trees. The suite encodes many compatibility contracts; changing text syntax requires broad updates.

Test signals: very strong coverage for parser recovery, `AUTO`, special pointers, strings/globs, out args, vma clamping, call props, comments, compressed image elision, and executor-equivalence preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encoding_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encodingexec.go -->
# sources/test-tools/syzkaller/prog/encodingexec.go

Purpose: serializes `Prog` into the compact executor binary instruction stream.

Important APIs/types/functions: executor op/arg constants, `ExecBufferSize`, `ExecNoCopyout`, `execMaxCommands`, `Prog.SerializeForExec`, `execContext.serializeCall`, `serializeKFuzzTestCall`, `writeCallProps`, `writeCopyin`, `willBeUsed`, `writeChecksums`, `writeCopyout`, `writeArg`, and `writeConstArg`.

Control flow and state: `SerializeForExec` validates, writes call count, serializes each call with fresh per-call checksum maps, writes EOF, and enforces buffer/copyout limits. Normal calls emit copyins, checksum copyins in reverse address order, call props, syscall instruction, result copyout ID if needed, top-level args, then post-call copyouts. `execContext` persists the byte buffer, arg address/copyout map, and global copyout sequence. KFuzzTest calls write the test-name copyin, marshal the struct argument into a relocation blob, copy it into a provided buffer, update the length arg, and defer final syscall emission.

Dependencies and integration: relies on `calcChecksumsCall`, `ForeachArg`, target physical addresses/data offset, `CallProps.ForeachProp`, `MarshallKFuzztestArg`, binary varint encoding, and arg/resource metadata.

Risks: this is an executor ABI; opcode/meta changes must stay synchronized with executor and `decodeexec.go`. Mutating the KFuzzTest length arg during serialization is observable if the caller reuses the program. Error from `serializeCall` is currently ignored in the main loop except for later size limits, preserving existing dashboard behavior. Incorrect `willBeUsed` bookkeeping causes missing copyouts or checksum data.

Test signals: `encodingexec_test.go` checks exact instruction streams for alignment, unions, arrays, endian formats, bitfields, resources, checksums, call props, copyout vars, random decodeability, and overflow errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encodingexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encodingexec_test.go -->
# sources/test-tools/syzkaller/prog/encodingexec_test.go

Purpose: verifies the executor binary format emitted by `encodingexec.go` and decoded by `decodeexec.go`.

Important APIs/types/functions: `TestSerializeForExecRandom`, `TestSerializeForExec`, and `TestSerializeForExecOverflow`.

Control flow and state: random tests generate programs, serialize for exec, decode them, validate call counts, and collect size histograms/stat accounting. Table tests construct expected varint streams from mixed uint64/int/blob elements and compare raw bytes. Selected cases also compare decoded `ExecProg` structs. Overflow tests synthesize programs that approach/exceed copyout command and buffer limits.

Dependencies and integration: uses `binary.AppendVarint`, `gohistogram`, target descriptions, text deserialization, `ExecCallCount`, `DeserializeExec`, and constants from serializer/decoder.

Risks: exact byte expectations are intentionally brittle because they define ABI behavior. Histogram output is diagnostic only. Large generated overflow cases must remain below test runtime/memory limits while exceeding serializer limits.

Test signals: strong byte-level coverage for copyin offsets, struct alignment, varlen arrays, unions, big-endian metadata, bitfields, proc values, special pointers, checksum chunks, call properties, resource copyout/copyin, and size guards.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/encodingexec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/export_test.go -->
# sources/test-tools/syzkaller/prog/export_test.go

Purpose: exposes selected internals and common target/random helpers for package tests.

Important APIs/types/functions: `init` sets `debug = true`; exported aliases `CalcChecksumsCall`, `InitTest`, and `initTargetTest`; helpers `initRandomTargetTest`, `initTest`, `testEachTarget`, `testEachTargetRandom`, `skipTargetRace`, and `initBench`.

Control flow and state: test initialization enables debug validation globally. Target iteration runs subtests in parallel, with race-mode filtering to keep CI runtime manageable. Random helpers provide deterministic testutil sources and iteration counts. `initBench` temporarily disables debug and returns a cleanup closure.

Dependencies and integration: imports `pkg/testutil`, target loading, and Go testing/benchmark APIs. Used throughout this subset's tests for target setup, randomness, checksum export, and benchmark setup.

Risks: global `debug` mutation affects all package tests and must be restored in benchmarks. Parallel target tests require helpers to avoid shared mutable target state bugs. Race-mode filtering may reduce architecture coverage.

Test signals: this file is infrastructure rather than a test subject; failures in many tests would expose broken helper behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/expr.go -->
# sources/test-tools/syzkaller/prog/expr.go

Purpose: evaluates conditional expressions and maintains conditional union fields during generation, mutation, deserialization, validation, and minimization.

Important APIs/types/functions: `BinaryExpression.Evaluate`, `Value.Evaluate`, `makeArgFinder`, `randGen.patchConditionalFields`, `forEachStaleUnion`, `checkUnionArg`, `matchingUnionArgs`, `Prog.checkConditions`, `ErrViolatedConditions`, `Call.checkConditions`, and `Call.setDefaultConditions`.

Control flow and state: expression evaluation recursively computes boolean/bitwise operators, resolving path-based values through an `ArgFinder`. Conditional patching loops until no stale unions remain, generating replacement args and extra resource-constructor calls as needed. `forEachStaleUnion` walks call args with parent stack, skips `ANY` pointers, evaluates current union options, and reports stale or transient unions with matching alternatives. Default-setting replaces stale unions with default or first matching field defaults until stable.

Dependencies and integration: depends on compiler expression/field metadata, target `findArg`, `SquashedArgFound`, arg replacement, random generation, traversal with parent stack, and minimization integer reset logic.

Risks: nested conditional patching is guarded by a depth panic. Missing matching union fields panic because descriptions should include a fallback. Expressions that reference squashed `ANY` args are treated as uncalculable, preserving existing choices. Incorrect default elision can silently violate conditions.

Test signals: `expr_test.go` covers generation, mutation, strict validation errors, conditional resource stress, minimization interactions, nested conditions, conditional unions, and serialize/deserialize preservation of default selected options.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/expr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/expr_test.go -->
# sources/test-tools/syzkaller/prog/expr_test.go

Purpose: validates conditional-field generation, mutation, evaluation, minimization, nesting, and serialization stability.

Important APIs/types/functions: tests include `TestGenerateConditionalFields`, `TestConditionalResources`, `TestMutateConditionalFields`, `TestEvaluateConditionalFields`, `TestConditionalMinimize`, `TestConditionalUnionFields`, `TestNestedConditionalCall`, `TestDefaultConditionalSerialize`, plus helpers `genConditionalFieldProg`, `validateConditionalProg`, and `parseConditionalStructCall`.

Control flow and state: tests generate and mutate programs using test target descriptions, inspect union selections against mask bits, and assert strict deserialization rejects violated conditions with `ErrViolatedConditions`. Minimization tests use predicates that force condition-aware defaulting or retention.

Dependencies and integration: uses `newRand`, `newState`, `ChoiceTable`, `Deserialize`, `Serialize`, `Minimize`, `testify`, and conditional descriptions in the `test/64` target.

Risks: random coverage thresholds are modest and can miss rare conditional combinations, but deterministic table cases cover core semantics. Exact serialized output makes default-elision behavior explicit.

Test signals: strong coverage for parent-path expressions, nested conditional structs, conditional unions, transient defaults, mutation sanitation, and minimizer interaction with condition-changing integer resets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/expr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/generation.go -->
# sources/test-tools/syzkaller/prog/generation.go

Purpose: provides the public random program generation entry point.

Important APIs/types/functions: `Target.Generate(rs rand.Source, ncalls int, ct *ChoiceTable) *Prog`.

Control flow and state: creates an empty `Prog`, a `randGen`, and a fresh analysis `state`. It repeatedly calls `generateCall`, analyzes every generated call, and appends calls until at least `ncalls`. If resource-creating helper calls overflow the requested count, it removes calls at `ncalls-1` until count matches, allowing affected resources in the final call to fall back to defaults. Finally it sanitizes/fixes and debug-validates the program.

Dependencies and integration: depends on `newRand`, `newState`, `generateCall`, state analysis, `RemoveCall`, `sanitizeFix`, and `debugValidate`. Used by random tests, fuzzing, mutation tests, checksum tests, and serialization round trips.

Risks: removing overflow helper calls can change resource availability and relies on `RemoveCall` cleanup/defaulting. Generation quality depends on accurate analysis state and choice tables.

Test signals: many tests use `Generate`; random serialization, checksum, conditional, hints, minimization, and executor tests indirectly stress this path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/generation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/heatmap.go -->
# sources/test-tools/syzkaller/prog/heatmap.go

Purpose: defines mutation heatmaps that bias byte mutations toward non-uniform data regions.

Important APIs/types/functions: `Heatmap` interface, `MakeGenericHeatmap`, `GenericHeatmap.NumMutations`, `GenericHeatmap.ChooseLocation`, `segment`, `calculateLengthAndSegments`, and `translateIdx`.

Control flow and state: construction splits data into 64-byte chunks, groups contiguous chunks that are not a single repeated byte into segments, and falls back to one full-data segment if all chunks are constant. `ChooseLocation` selects uniformly within concatenated interesting segments and translates back to raw index. `NumMutations` uses random counts based on heatmap length, with a hard cap of 10.

Dependencies and integration: uses `math/rand`; intended for mutating large blobs/images where uniform random byte selection wastes effort on padding or constant areas.

Risks: panics on empty data and out-of-range translated indexes. Granularity can skip small interesting changes inside otherwise constant chunks or include noise in mixed chunks. Mutation count is randomized and heuristic.

Test signals: `heatmap_test.go` decodes representative base64 data and asserts chosen indexes stay within expected interesting regions, including all-constant fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/heatmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/heatmap_test.go -->
# sources/test-tools/syzkaller/prog/heatmap_test.go

Purpose: validates generic heatmap segment selection and index translation.

Important APIs/types/functions: `TestGenericHeatmap`, `checkIndex`, `region`, and `GenericHeatmap.debugPrint`.

Control flow and state: test cases provide base64-encoded data and allowed raw regions. The test decodes data, builds heatmaps over many iterations, samples locations, and fails with debug dumps if any selected index falls outside allowed regions. An all-constant input verifies fallback to uniform full-data coverage.

Dependencies and integration: uses `pkg/image.DecodeB64`, `pkg/testutil` iteration/rand helpers, and private heatmap internals for debug output.

Risks: probabilistic sampling may not exercise every segment boundary each run, but any invalid selected region is caught. Expected regions are tied to current `granularity`.

Test signals: confirms sparse non-constant segment detection, all-constant fallback, raw bounds checking, and debug visibility for failed segment maps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/heatmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/hints.go -->
# sources/test-tools/syzkaller/prog/hints.go

Purpose: implements comparison-guided mutation hints that replace program argument values with values observed in executor comparison feedback.

Important APIs/types/functions: `CompMap` with `Add`, `String`, `Len`, `InplaceIntersect`; `Prog.MutateWithHints`; `generateHints`; `checkConstArg`; `checkDataArg`; `checkCompressedArg`; `shrinkExpand`; `HintsLimiter.Limit`; `specialIntsSet` initialization.

Control flow and state: `MutateWithHints` clones the program, iterates args in one call, generates candidate replacements, sanitizes and condition-checks each candidate, validates it, then invokes the callback until it returns false. Const/data checks derive replacement values through `shrinkExpand`, which models integer narrowing, sign extension, big-endian matching, bit-size limits, and special-int filtering. Compressed images are decompressed, mutated only at aligned 4/8-byte offsets, recompressed per candidate, and restored afterward. `HintsLimiter` maintains global per-PC attempt counts behind a mutex and prunes comparison entries beyond 10 attempts.

Dependencies and integration: uses traversal, sanitization, conditional checks, resource/type `uselessHint` filters, image compression, endian swap helpers, `specialInts`, and mutation execution callbacks from the fuzzer.

Risks: candidate volume can explode without limiter and cutoffs. Mutation order is partly map-derived but final replacers are sorted in `shrinkExpand`. Compressed-image mutation must carefully release decompressed buffers and restore original data. Skipping invalid conditional candidates avoids deep repairs but may miss useful hints.

Test signals: `hints_test.go` covers const/data/blob/compressed replacements, shrink/expand semantics, big-endian matching, call-level filtering, random validation, intersection, limiter accumulation, and benchmark behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/hints.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/hints_test.go -->
# sources/test-tools/syzkaller/prog/hints_test.go

Purpose: validates comparison-guided hint mutation behavior across constants, data blobs, compressed images, complete calls, random programs, map intersection, and limiter state.

Important APIs/types/functions: `ConstArgTest`, `DataArgTest`, `TestHintsCheckConstArg`, `TestHintsCheckDataArg`, `TestHintsCompressedImage`, `TestHintsShrinkExpand`, `TestHintsCall`, `TestHintsRandom`, `extractValues`, `TestHintsData`, `TestInplaceIntersect`, `BenchmarkHints`, `TestHintsLimiter`, `perPCCount`, and `compSet`.

Control flow and state: table tests build synthetic `CompMap` values and assert exact replacements. Random tests generate programs, extract scalar/blob values, build comparison maps, and run `MutateWithHints` for validation. Limiter tests apply two rounds to prove per-PC counts accumulate and prune later maps.

Dependencies and integration: uses `image.Compress/MustDecompress`, target test descriptions, `Deserialize`, `Serialize`, `ForeachArg`, `newRand`, benchmarks, and `testify`.

Risks: exact expected mutations depend on `specialInts`, endian swap behavior, and sorted replacer order. Random tests skip oversized programs/calls to bound quadratic validation cost.

Test signals: very strong coverage of shrink/extend edge cases, bit sizes, negative values, special-int filtering, big-endian replacement, compressed image alignment, call-specific useless-hint filtering, and limiter pruning.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/hints_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/images_test.go -->
# sources/test-tools/syzkaller/prog/images_test.go

Purpose: verifies extraction of compressed filesystem image assets from programs.

Important APIs/types/functions: package-level `flagUpdate` and `TestForEachAsset`.

Control flow and state: the test loads Linux/amd64, scans `testdata/fs_images/*.in`, deserializes each program, calls `Prog.ForEachAsset`, reads each asset stream, optionally updates golden output files, compares bytes to `*.out_mount_N`, and verifies every existing output file was used.

Dependencies and integration: uses `GetTarget`, `Deserialize`, `ForEachAsset`, `AssetType`, `MountInRepro`, `osutil.WriteFile`, filesystem testdata, and `testify/require`.

Risks: `-update` mutates golden files intentionally. The test is sensitive to testdata layout and asset naming (`mount_<call index>`). It assumes compressed image deserialization succeeds before asset extraction.

Test signals: direct coverage for compressed image decompression, asset callback metadata, syscall association, output naming, and completeness of golden assets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/kfuzztest.go -->
# sources/test-tools/syzkaller/prog/kfuzztest.go

Purpose: serializes syzkaller argument trees into the KFuzzTest kernel module's flat region/relocation/payload input format.

Important APIs/types/functions: constants for magic/version/alignment/max input; `kFuzzTestWritePrefix`, `isPowerOfTwo`, `roundUpPowerOfTwo`, `padWithAlignment`; generic `sliceQueue`; `kFuzzTestRelocation`, `kFuzzTestRegion`; region/relocation table writers; `kFuzzTestExpandRegion`; and public `MarshallKFuzztestArg`.

Control flow and state: `kFuzzTestExpandRegion` breadth-first expands one logical region, aligns each arg, writes placeholder pointers and relocation records, appends group children, null-terminates string buffers, writes constants by size, and rejects unsupported arg kinds. `MarshallKFuzztestArg` walks reachable regions once, computes region offsets/sizes and relocations, pads each payload region with poison redzones, computes metadata padding for maximum alignment, then writes prefix, region array, relocation table, and payload.

Dependencies and integration: used by `encodingexec.go` for `KFuzzTest` syscalls. Depends on arg concrete types, type alignment, little-endian binary layout, and kernel header format documented in comments.

Risks: unsupported union args and unusual constant sizes panic. Region IDs are derived from visited map order during BFS, so ordering changes affect ABI/tests. `uint32` offsets/sizes assume encoded inputs stay below KFuzzTest max size. String null-termination mutates a local slice, not the original arg.

Test signals: `kfuzztest_test.go` checks power-of-two rounding and exact prefix/region-array/relocation-table/payload bytes for pointer-heavy and flat struct examples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/kfuzztest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/kfuzztest_test.go -->
# sources/test-tools/syzkaller/prog/kfuzztest_test.go

Purpose: validates KFuzzTest binary argument marshalling.

Important APIs/types/functions: `testCase`, `TestRoundUpPowerOfTwo`, `createBuffer`, `createPrefix`, `TestMarshallKFuzzTestArg`, and `testOne`.

Control flow and state: tests deserialize Linux/amd64 programs, extract a specific arg tree, call `MarshallKFuzztestArg`, independently build expected prefix/region array/relocation table/payload byte slices, split the encoded output by expected lengths, and compare each segment.

Dependencies and integration: uses target deserialization, `encoding/binary`, KFuzzTest constants, and `testify/assert`.

Risks: exact byte arrays are long and sensitive to region ordering, padding, alignment, and kernel format changes. The tests currently cover pointer/group/data/const paths but not unsupported unions or cyclic references beyond visited-region behavior.

Test signals: strong ABI-level checks for magic/version prefix, region counts/offsets/sizes, relocation null/destination IDs, metadata padding, payload alignment, string/data/const serialization, and tail poison padding.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/kfuzztest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/little_endian.go -->
# sources/test-tools/syzkaller/prog/little_endian.go

Purpose: provides the package-level host byte order for supported little-endian builds.

Important APIs/types/functions: under build tags `amd64 || 386 || arm64 || arm || mips64le || ppc64le || riscv64`, declares `var HostEndian = binary.LittleEndian`.

Control flow and state: no runtime control flow; architecture build tags select this file. `HostEndian` is global immutable-by-convention state.

Dependencies and integration: imports `encoding/binary`; paired with `big_endian.go`. Code needing target byte order should still rely on type `BinaryFormat`, not host endianness.

Risks: new little-endian architectures need build-tag updates. Duplicate or missing tags would cause compile failures or wrong host encoding.

Test signals: no direct tests; most CI architectures indirectly compile this file, and executor serialization tests cover explicit big-endian target formats separately.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/little_endian.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/meta.go -->
# sources/test-tools/syzkaller/prog/meta.go

Purpose: stores build-time git revision metadata for diagnostics and panic context.

Important APIs/types/functions: `defaultGitRevision`, globals `GitRevision`, `GitRevisionBase`, `gitRevisionDate`, `GitRevisionDate`, `GitRevisionKnown`, and `init`.

Control flow and state: at init time, strips `+` from `GitRevision` to form `GitRevisionBase`, and parses non-empty `gitRevisionDate` with layout `20060102-150405`, panicking on parse failure. `GitRevisionKnown` reports whether the Makefile injected a non-default revision.

Dependencies and integration: `encoding.go` includes `GitRevision` in deserialization panic context. Build/link steps are expected to fill the globals.

Risks: malformed injected date panics at package init. Unknown revision is normal in ad hoc builds but reduces diagnostic precision.

Test signals: no direct tests in this subset; behavior is simple and indirectly visible in deserialization panic wrapping.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/meta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/minimization.go -->
# sources/test-tools/syzkaller/prog/minimization.go

Purpose: reduces programs while preserving an external equivalence predicate, supporting corpus minimization, crash reproducer minimization, snapshot-mode readability, and calls-only mode.

Important APIs/types/functions: stats variables, `MinimizeMode`, `Minimize`, `removeCalls`, `removeUnrelatedCalls`, `relatedCalls`, `uses`, `resetCallProps`, `minimizeCallProps`, `minimizeArgsCtx.do`, and type-specific `minimize` methods for structs, unions, pointers, arrays, ints/flags/procs, resources, and buffers.

Control flow and state: `Minimize` wraps the predicate with sanitize/debug/dedup/stat accounting, records target call identity, removes calls, optionally resets/minimizes props and args, and restarts per-call traversal after each committed simplification. Call removal tries trailing calls, unrelated resource/file-connected calls, then individual reverse removals. Arg minimization mutates a cloned working program, asks the predicate, commits by replacing `*p0`, and tracks tried paths to avoid duplicates.

Dependencies and integration: depends on `Clone`, `RemoveCall`, `ForeachArg`, resource `uses`, filename buffers, target size assignment, conditional defaulting, hash/stat packages, and serialization for dedup.

Risks: minimization mutates candidate trees in place; stale-tree and shared-program panics guard commit protocol. Modes intentionally skip expensive or readability-focused reductions. Compressed buffers under `no_minimize` calls panic if reached. Resource and condition changes require careful restoration on failed predicates.

Test signals: `minimization_test.go` covers call removal, resource replacement, props retention/removal, pointer/pointee minimization, filename shortening, no-minimize calls, unrelated-call pruning, random duplicate avoidance, and call-index preservation. `expr_test.go` covers conditional interactions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/minimization.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/minimization_test.go -->
# sources/test-tools/syzkaller/prog/minimization_test.go

Purpose: validates program minimization behavior across deterministic scenarios and randomized invariants.

Important APIs/types/functions: `TestMinimize`, `TestMinimizeRandom`, and `TestMinimizeCallIndex`.

Control flow and state: `TestMinimize` is table-driven and feeds input programs, modes, target call indexes, and custom predicates into `Minimize`, then compares serialized output and resulting call index. Random tests generate programs, track candidate hashes to reject duplicates, randomly accept/reject candidates, and ensure committed output matches the last accepted clone. Call-index tests ensure target call identity survives random minimization.

Dependencies and integration: uses target deserialization/generation, `Minimize`, `Serialize`, `Clone`, `hash.String`, random sources, and Linux/test target descriptions.

Risks: deterministic cases depend on exact serializer output and on the sequence of minimization attempts for unrelated-call pruning. Random tests divide iterations to limit runtime and may miss rare cases.

Test signals: strong coverage for false predicates, removing calls/dependencies, resource defaulting, pointer removal versus pointee minimization, props handling (`fail_nth`, `async`, `rerun`), filename shrinkage, `NoMinimize`, unrelated-call transitive closure, duplicate candidate suppression, and call-index stability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/minimization_test.go -->
