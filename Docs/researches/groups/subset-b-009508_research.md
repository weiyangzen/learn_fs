# subset-b-009508 grouped research

This grouped report covers the requested syzkaller `prog` and `sys` files. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/mutation.go -->
## sources/test-tools/syzkaller/prog/mutation.go

Purpose: implements program mutation for syzkaller programs, including whole-program operations and per-argument mutations. It is the main fuzzing evolution engine after generation.

Important APIs/types/functions: `Prog.Mutate`, `Prog.MutateWithOpts`, `MutateOpts`, `mutator`, `splice`, `squashAny`, `insertCall`, `removeCall`, `mutateArg`, `chooseCall`, `Target.mutateArg`, per-type `mutate` methods, `mutationArgs`, mutation-priority methods, `mutateData`, `loadInt`, `storeInt`, and endian swap helpers.

Control flow: `MutateWithOpts` builds a `randGen`, normalizes the call limit, then repeatedly selects a weighted operation until the expected-iteration stop condition fires. Insert and argument mutation analyze existing state before generating support calls, splice clones corpus programs, removal fixes resource users through `RemoveCall`, and final `sanitizeFix` plus debug validation enforce invariants.

State and persistence: all state is in-memory on `Prog`, `Call`, and `Arg` graphs. Resource use links are updated via `replaceArg`, `removeArg`, and `replaceResultArg`. Blob and compressed-image mutations alter `DataArg` data, and pointer allocations may move when pointee size grows.

Dependencies/integration: depends on `rand.go` generation, `state` analysis, `size.go` length assignment, `image` compression for filesystem images, choice-table selection from `prio.go`, and type definitions from `types.go`.

Risks: mutation relies on correct resource link repair; a missed `removeArg` can leave dangling users. Compressed-image mutation must not target empty decompressed data. Size mutations intentionally make invalid lengths but must preserve decompression safety. A notable risk in nearby generation logic used by mutation is `resourceCentric` in `rand.go`, where a biased length is calculated from `len(calls)` even though the local `calls` slice is nil, which can panic if that path is reached.

Test signals: `mutation_test.go` checks flags, argument priority, no-squash behavior, length mutation bounds, clone immutability, corpus mutation, table-driven mutation goals, negative mutations, and store/load helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/mutation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/mutation_test.go -->
## sources/test-tools/syzkaller/prog/mutation_test.go

Purpose: validates that mutation can reach expected program transformations while preserving program validity and source-program immutability.

Important APIs/types/functions: `TestMutationFlags`, `TestChooseCall`, `TestMutateArgument`, `TestMutateNoSquash`, `TestSizeMutateArg`, `TestClone`, `TestMutateRandom`, `TestMutateCorpus`, `TestMutateTable`, `TestNegativeMutations`, `runMutationTests`, `buildTestContext`, and benchmarks for mutation/generation and integer store/load.

Control flow: table tests deserialize an original program and a goal program, build a choice table from the union of involved syscalls, mutate cloned originals with a deterministic random source, and compare serialized output. Random tests generate programs, mutate clones, deserialize mutated output, and ensure the original serialization is unchanged.

State and persistence: no persistent state. It exercises in-memory `Prog` clone, mutation, serialization, and deserialization state. The test helpers use deterministic `rand.Source` values to make probability-heavy mutation paths reproducible enough for goal-seeking loops.

Dependencies/integration: integrates with test target descriptions, `testutil.IterCount`, choice tables, serialization/deserialization, clone, and length assignment.

Risks: many tests are probabilistic and use high iteration counts, so they can be slow and are skipped under race mode in selected cases. Goal tests assert reachability, not exact distribution quality. Negative mutation tests guard against out-of-range ranged-buffer sizes.

Test signals: this file itself is the principal signal for mutation. It covers both focused table goals and randomized full-target mutation, plus benchmark coverage for hot paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/mutation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/parse.go -->
## sources/test-tools/syzkaller/prog/parse.go

Purpose: extracts serialized syzkaller programs from executor/manager logs and records offsets, proc IDs, optional program IDs, and legacy fault-injection metadata.

Important APIs/types/functions: `LogEntry`, `Target.ParseLog`, and `extractInt`.

Control flow: `ParseLog` scans line by line. A line containing `executing program ` starts a new entry and finalizes the previous one if a program was parsed. Other lines are appended to a candidate buffer and repeatedly passed to `Deserialize`; the newest successfully parsed program becomes the current entry. Legacy `fault-call` and `fault-nth` markers are translated into `CallProps.FailNth`.

State and persistence: parsing is stateless beyond local offsets, current buffer, current entry, and pending fault metadata. It returns in-memory `LogEntry` objects and does not write data.

Dependencies/integration: uses target-specific `Deserialize` modes. Consumers rely on `Start` and `End` offsets for crash triage and log extraction.

Risks: partial log parsing intentionally ignores deserialization errors until a larger buffer succeeds. The newline handling for data without a trailing newline uses `len(data)-1` and should be considered carefully for empty or malformed inputs. `extractInt` ignores `Atoi` errors after selecting digit-only spans.

Test signals: `parse_test.go` covers single logs, modern and legacy multi-program logs, proc and id extraction, offsets, and legacy fault property conversion.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/parse_test.go -->
## sources/test-tools/syzkaller/prog/parse_test.go

Purpose: verifies log parsing behavior for single programs, modern logs with IDs, legacy logs without IDs, unrelated kernel text between program lines, and old fault-injection annotations.

Important APIs/types/functions: `TestParseSingle`, `TestParseMulti`, `TestParseMultiLegacy`, `validateProgs`, `TestParseFault`, and embedded `execLogNew`/`execLogOld` fixtures.

Control flow: tests get the linux/amd64 target, parse static log text with `NonStrict`, validate entry counts, offsets, proc numbers, IDs, program call names, and absence of new fault-injection features except for converted legacy metadata.

State and persistence: no persistence. Test data is in string constants and parsed into in-memory `LogEntry` and `Prog` objects.

Dependencies/integration: depends on generated linux target registration and serializer string forms such as `getpid-gettid`.

Risks: expected program strings couple tests to syscall names and serialization output. The fault test documents a compatibility adjustment from zero-based legacy fault nth to one-based `FailNth`.

Test signals: strong regression signal for parser compatibility across log formats and for offset accounting needed by crash report extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prio.go -->
## sources/test-tools/syzkaller/prog/prio.go

Purpose: computes syscall-to-syscall priorities used by generation to bias new calls toward combinations likely to produce coverage.

Important APIs/types/functions: `Target.CalculatePriorities`, `prepareEnabledSyscalls`, `calcStaticPriorities`, `calcResourceUsage`, `calcDynamicPrio`, `normalizePrios`, `ChoiceTable`, `BuildChoiceTable`, `ChoiceTable.Generatable`, and `ChoiceTable.choose`.

Control flow: enabled calls are filtered to exclude disabled and `NoGenerate` calls. Static priorities are built from shared resource, pointer, filename, string, and VMA usage. Dynamic priorities count ordered call pairs in corpus programs and dampen counts with square root. Both matrices are normalized to distribute `10 * enabled` points per row, then `ChoiceTable` stores cumulative rows for weighted binary-search selection.

State and persistence: stores only in-memory priority matrices and choice-table cumulative rows. No persistent state.

Dependencies/integration: depends on `ForeachType`, syscall metadata, resource descriptors, corpus programs, and `randGen.generateCall`.

Risks: constants are heuristic and can bias fuzzing quality. Sparse enabled sets can produce rows with low or zero priorities; self-priority fallback handles fully isolated calls. Debug mode checks no disabled call has nonzero priority.

Test signals: `prio_test.go` covers normalization, static priorities, determinism, and benchmarks choice-table construction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prio_test.go -->
## sources/test-tools/syzkaller/prog/prio_test.go

Purpose: validates priority normalization, static resource-based priority calculation, deterministic choice-table behavior, and performance.

Important APIs/types/functions: `TestNormalizePrios`, `TestStaticPriorities`, `TestPrioDeterminism`, and `BenchmarkBuildChoiceTable`.

Control flow: tests build small priority matrices or target choice tables, run normalization/calculation, and compare expected weights or repeated outputs under identical seeds.

State and persistence: in-memory only. Random sources are deterministic for reproducibility.

Dependencies/integration: relies on test target metadata and `BuildChoiceTable`.

Risks: deterministic tests guard ordering and random choice stability, but they do not prove priority quality for fuzzing effectiveness.

Test signals: useful for catching accidental changes to normalization math, enabled-call filtering, and map-order nondeterminism.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prog.go -->
## sources/test-tools/syzkaller/prog/prog.go

Purpose: defines the core in-memory program representation: programs, calls, argument implementations, resource links, mutation-safe replacement/removal helpers, sanitization, and human-readable argument formatting.

Important APIs/types/functions: `Prog`, `CallProps`, `Call`, `MakeCall`, `Arg`, `ArgCommon`, `ConstArg`, `PointerArg`, `DataArg`, `GroupArg`, `UnionArg`, `ResultArg`, constructors for each arg kind, `InnerArg`, `replaceArg`, `replaceResultArg`, `removeArg`, `RemoveCall`, `FormatArg`, `sanitize`, and `CallProps.ForeachProp`.

Control flow: constructors assign type refs and directions. Replacement copies concrete arg data while repairing resource use maps. Removing an arg walks all subargs, deletes incoming resource links, and resets users to defaults. `RemoveCall` removes all call arguments and return values before slicing the call list. `FormatArg` recursively renders structured args.

State and persistence: owns mutable in-memory program state. `ResultArg.uses` is the main internal cross-link structure. `Prog.isUnsafe` relaxes validation for special data-mmap programs.

Dependencies/integration: used by all generation, mutation, serialization, validation, minimization, and execution encoding paths.

Risks: any shallow copy or missed resource-link update can corrupt the graph. `replaceArg` has special structure-preserving behavior for structs but allows array length changes. `DataArg` clones input data on construction/set to avoid accidental aliasing.

Test signals: `prog_test.go`, `mutation_test.go`, validation, serialization, and fuzz tests exercise constructors, clone stability, defaults, special structs, and cross-target serialization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prog_test.go -->
## sources/test-tools/syzkaller/prog/prog_test.go

Purpose: broad integration tests for generation, default arguments, serialization round trips, VMA length handling, target attributes, cross-target deserialization, special type generators, path safety, fallback signal generation, sanitization, and recursion pruning.

Important APIs/types/functions: `TestGeneration`, `TestDefault`, `TestDefaultCallArgs`, `testSerialize`, `TestVmaType`, `TestFsckAttr`, `TestCrossTarget`, `testCrossTarget`, `testCrossArchProg`, `TestSpecialStructs`, `TestEscapingPaths`, `TestFallbackSignal`, `TestSanitizeRandom`, and `TestPtrRecursion`.

Control flow: tests use target initialization helpers, generate or deserialize programs, serialize/deserialize them in strict and non-strict modes, mutate/minimize for cross-target validation, and verify expected syscall/argument behavior.

State and persistence: no persistence. Tests exercise generated in-memory target state and program graphs.

Dependencies/integration: integrates with all registered targets, target-specific special generators, fallback signal code, minimization, mutation, and serializer/deserializer.

Risks: cross-target testing is O(N^2) in argument count and filters large programs. Some tests skip under race mode or reduce iterations in short mode. Expected serialization can be sensitive to description changes.

Test signals: high-value smoke and regression coverage across the `prog` package and target registry.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/prog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rand.go -->
## sources/test-tools/syzkaller/prog/rand.go

Purpose: implements random program, call, argument, resource, filename, buffer, text, and pseudo-syscall generation.

Important APIs/types/functions: `randGen`, `newRand`, probability helpers, `randInt`, `truncateToBitSize`, `flags`, filename/string generators, allocation helpers, recursion pruning, `createResource`, `generateText`, `generateCall`, `generateParticularCall`, `Target.GenerateAllSyzProg`, `PseudoSyscalls`, `GenSampleProg`, `DataMmapProg`, `generateArgs`, `generateArgImpl`, and per-type `generate` methods.

Control flow: generation chooses calls from a `ChoiceTable`, creates a `Call`, recursively generates typed arguments, patches conditional fields, assigns sizes, and returns prerequisite calls before the final call. Resource generation prefers existing resources, then corpus-derived/resource-centric resources, then constructors, then special constants. Buffer and text generation use kind-specific strategies.

State and persistence: uses in-memory `state` for resources, files, strings, memory allocation, VMA allocation, corpus, and choice table. `randGen` tracks recursion depth and KFuzzTest/resource-generation modes.

Dependencies/integration: integrates with `prio.go`, `resources.go`, `size.go`, `mutation.go`, ifuzz, image compression, target special type hooks, and memory allocation utilities.

Risks: recursive type generation must be bounded to avoid exponential trees. Filename generation must not escape the sandbox. Resource construction can generate support calls and requires correct state analysis. The `resourceCentric` function appears to compute `biasedLen` from `len(calls)` rather than `len(p.Calls)`, making the path vulnerable to a negative argument to `biasedRand`.

Test signals: `rand_test.go`, `resources_test.go`, `prog_test.go`, and fuzz tests cover determinism, enabled/no-generate constraints, integer bounds, filenames, resource creation, and serialization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rand_test.go -->
## sources/test-tools/syzkaller/prog/rand_test.go

Purpose: validates random generation and mutation determinism, filename sandbox safety, enabled-call enforcement, integer bit bounds, flags distribution visibility, truncation, and `NoGenerate` behavior.

Important APIs/types/functions: `TestNotEscaping`, `TestDeterminism`, `generateProg`, `TestEnabledCalls`, `TestSizeGenerateConstArg`, `TestFlags`, `TestTruncateToBitSize`, and `TestNoGenerate`.

Control flow: deterministic tests replay the same seed through generation, mutation, hints, minimization, serialization, and deserialization. Enabled/no-generate tests build restricted choice tables and verify generated/mutated programs stay within allowed syscall sets.

State and persistence: in-memory only. Deterministic seeds and generated corpus lists are local to tests.

Dependencies/integration: depends on hint mutation, minimization, serialization, deserialization, target choice tables, and test target setup.

Risks: distribution tests mostly log observations instead of asserting exact ratios. Determinism checks can be sensitive to map iteration unless production code sorts keys, which this subset generally does.

Test signals: strong coverage for random-source reproducibility and safety constraints that protect fuzzing runs from invalid programs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/resources.go -->
## sources/test-tools/syzkaller/prog/resources.go

Purpose: computes resource constructors, resource compatibility, input resources, and the transitive set of syscalls that can be generated when dependencies are satisfied.

Important APIs/types/functions: `timespecRes`, `filenameRes`, `vmaRes`, `Target.calcResourceCtors`, `populateResourceCtors`, `isCompatibleResource`, `isCompatibleResourceImpl`, `getInputResources`, `transitivelyEnabled`, and `TransitivelyEnabledCalls`.

Control flow: `populateResourceCtors` scans syscall types to collect created resources, used resources, and input resources, adds special `clock_gettime` support for timespec, then populates precise and imprecise constructors based on resource-kind prefix compatibility. Transitive enablement repeatedly adds calls whose input resources can already be created.

State and persistence: fills per-target in-memory syscall fields (`inputResources`, `createsResources`, `usesResources`) and resource constructor lists.

Dependencies/integration: depends on restored resource descriptors, `ForeachCallType`, target OS checks, and is used by generation, rotation, and enabled-call filtering.

Risks: optional resources are intentionally skipped for dependency disabling; mistakes can over-disable or under-disable syscalls. Compatibility is prefix-based, so resource kind ordering is critical.

Test signals: `resources_test.go` checks constructor availability, linux epoll dependency behavior, automatic calls, optional resource handling, timespec disabling via `clock_gettime`, resource creation under rotated and partial syscall sets, and precise constructor preference.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/resources_test.go -->
## sources/test-tools/syzkaller/prog/resources_test.go

Purpose: validates resource constructor discovery, transitive syscall enablement, optional input handling, special linux resources, and generator resource creation.

Important APIs/types/functions: `TestResourceCtors`, `TestTransitivelyEnabledCalls`, `TestTransitivelyEnabledCallsLinux`, `TestTransitivelyEnabledAutoCalls`, `TestGetInputResources`, `TestClockGettime`, `TestCreateResourceRotation`, `TestCreateResourceHalf`, `testCreateResource`, and `TestPreferPreciseResources`.

Control flow: tests enumerate target resources and syscalls, remove selected constructors, compare disabled reasons, run resource creation for every input resource in enabled call sets, and count constructor preferences over repeated generation.

State and persistence: in-memory target metadata and generated calls only.

Dependencies/integration: integrates resource code with generated targets, rotator selection, choice tables, and random generation.

Risks: linux-specific counts are tied to current descriptions. Random preference checks use thresholds rather than exact distributions.

Test signals: strong coverage for dependency correctness, especially preventing generation of calls whose required resources cannot be produced.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rotation.go -->
## sources/test-tools/syzkaller/prog/rotation.go

Purpose: selects a random but dependency-aware subset of syscalls for corpus rotation/focused fuzzing.

Important APIs/types/functions: `Rotator`, `rotatorResource`, `MakeRotator`, `Rotator.Select`, `rotatorState`, `rotatorState.Select`, `addCall`, and `selectCalls`.

Control flow: construction classifies calls by resource inputs/outputs, adds synthetic filename/VMA resources, groups precise/imprecise constructors and uses, and sets a goal capped at 200 calls. Selection starts with resourceless calls, then repeatedly processes top resources and dependency resources, selecting constructors and users with probabilities until transitive enablement reaches the goal.

State and persistence: selection is in-memory and deterministic for a given random source and call set. No persistent state.

Dependencies/integration: depends on resource metadata populated in `resources.go`, `ForeachCallType`, and target transitive enablement.

Risks: probability heuristics can skew coverage. Dependency and top-resource queues need deterministic ordering before shuffling to avoid map-order nondeterminism. Empty resource sets return all calls.

Test signals: `rotation_test.go` checks resourceless behavior, selected subset validity, broad coverage over repeated selections, and determinism.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rotation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rotation_test.go -->
## sources/test-tools/syzkaller/prog/rotation_test.go

Purpose: verifies syscall rotation correctness, coverage, and deterministic behavior.

Important APIs/types/functions: `TestRotationResourceless`, `TestRotationRandom`, `TestRotationCoverage`, `selectCalls`, and `TestRotationDeterminism`.

Control flow: tests build call sets of varying size, run `MakeRotator(...).Select()`, ensure selected calls are a subset of original calls, repeat selections until all eligible calls are seen, and compare identical-seed outputs.

State and persistence: in-memory maps of syscalls and counters. No persistence.

Dependencies/integration: uses target metadata, resource transitive enablement, deterministic sorting, and `testify/require`.

Risks: coverage test uses 10,000 iterations and can still be probabilistic, though deterministic random sources reduce flakiness. Tests log selected calls for diagnosis.

Test signals: good guard against nondeterministic map iteration and dependency-breaking subset selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/rotation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/size.go -->
## sources/test-tools/syzkaller/prog/size.go

Purpose: assigns and mutates `LenType`/offset arguments based on referenced fields, parent structs, syscall arguments, arrays, VMAs, and bit-size units.

Important APIs/types/functions: `ParentRef`, `SyscallRef`, `Target.assignSizes`, `assignArgSize`, `assignSize`, `foundArg`, `findFieldStruct`, `findArg`, `computeSize`, `assignSizesArray`, `assignSizesCall`, and `randGen.mutateSize`.

Control flow: assignment walks call arguments and nested subargs with parent stacks. For each length arg it resolves the configured path, computes length or offset in units, and writes the constant. `findArg` handles overlays, parents, template-name parent references, and squashed ANY pointers. Mutation intentionally perturbs sizes while avoiding unsupported paths and compressed images.

State and persistence: mutates in-memory `ConstArg.Val` fields. `autos` can restrict which auto-size args are assigned.

Dependencies/integration: depends on `ForeachSubArg` with parent stacks, type metadata, pointer inner args, and mutation generation.

Risks: path resolution panics for invalid descriptions. Squashed ANY pointers leave sizes unchanged. Mutating compressed-image sizes is blocked because decompression assumes valid data.

Test signals: `size_test.go` covers randomized idempotence and a large table of path, parent, syscall, VMA, bit-size, offset, union, and squashed-arg cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/size_test.go -->
## sources/test-tools/syzkaller/prog/size_test.go

Purpose: verifies automatic length and offset assignment for many syzlang patterns.

Important APIs/types/functions: `TestAssignSizeRandom` and `TestAssignSize`.

Control flow: random tests generate and mutate programs, reassign sizes, and ensure serialization remains stable or at least valid. Table tests deserialize specific programs, apply `assignSizesCall`, and compare serialized output with expected length/offset values.

State and persistence: in-memory programs only.

Dependencies/integration: uses `TestDeserializeHelper`, test target descriptions, serialization, mutation, and generated calls.

Risks: table expectations are tightly coupled to test target descriptions and serialization. The table is intentionally broad because length paths are easy to regress.

Test signals: very strong coverage for `LenType` semantics, including nested parents, syscall refs, VMAs, arrays, unions, offsets, and ANY squashing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/target.go -->
## sources/test-tools/syzkaller/prog/target.go

Purpose: defines target OS/arch metadata registration, lazy initialization, link restoration, glob handling, special-generation API, program builder, and KFuzzTest syscall lookup.

Important APIs/types/functions: `Target`, `RegisterTarget`, `GetTarget`, `AllTargets`, `Extend`, `lazyInit`, `initTarget`, `initUselessHints`, `initRelatedFields`, `GetConst`, `sanitize`, `RestoreLinks`, `restoreLinks`, `DefaultChoiceTable`, `NoAutoChoiceTable`, `RequiredGlobs`, `UpdateGlobs`, `requiredGlobs`, `populateGlob`, `Gen`, `Builder`, `MakeProgGen`, `Append`, `Allocate`, `AllocateVMA`, `Finalize`, and `KFuzzTestRunID`.

Control flow: targets are registered by `os/arch`, lazily filled with generated descriptions, linked, indexed, enriched with resource constructors and hints, then target-specific init hooks add mmap, neutralization, special types, and constants. `restoreLinks` assigns global type refs and replaces compiler `Ref` placeholders.

State and persistence: global `targets` map and atomic global `typeRefs` store type references. Per-target maps cache syscalls, constants, flags, resources, and default choice table.

Dependencies/integration: central integration point for generated sys descriptions, OS init packages, random generation, validation, serialization, and tools.

Risks: global type refs require locking and unique assignment. Lazy init order is important: arch init depends on filled maps. Special pointer and filename length bounds are validated to protect generation.

Test signals: `target_test.go`, `prog_test.go`, and package-wide tests cover glob behavior, initialization, choice tables, special types, and target access.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/target.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/target_test.go -->
## sources/test-tools/syzkaller/prog/target_test.go

Purpose: tests glob pattern helper behavior used by target buffer glob values.

Important APIs/types/functions: `TestRequiredGlobs` and `TestPopulateGlob`.

Control flow: tests pass colon-separated include/exclude patterns into `requiredGlobs` and `populateGlob`, then compare sorted results.

State and persistence: no state beyond local maps and slices.

Dependencies/integration: targets with `BufferGlob` types rely on these helpers through `RequiredGlobs` and `UpdateGlobs`.

Risks: pattern strings assume tokens are non-empty because production helpers index `tok[0]`. Exclusions only remove exact file names.

Test signals: focused coverage for include/exclude semantics and deterministic sorted output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/target_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test/fuzz.go -->
## sources/test-tools/syzkaller/prog/test/fuzz.go

Purpose: provides fuzz entry points for deserialization and log parsing using the syzkaller test target.

Important APIs/types/functions: `FuzzDeserialize`, `FuzzParseLog`, and package-level `fuzzTarget`/`fuzzChoiceTable`.

Control flow: `FuzzDeserialize` tries non-strict and strict deserialization, verifies non-strict is not stricter than strict, checks serialize/deserialize idempotence, clone equality, optional exec serialization/deserialization, and then mutates the program. `FuzzParseLog` returns 1 if arbitrary data yields any parsed log entries.

State and persistence: no persistence. The target and choice table are initialized once at package load.

Dependencies/integration: imports all sys targets for registration, uses `targets.TestOS/TestArch64`, serialization, exec serialization, clone, mutation, and parse-log code.

Risks: fuzzing intentionally feeds malformed inputs and panics on invariant violations. Return value from `FuzzParseLog` is a fuzzer signal, not a correctness result for production callers.

Test signals: `fuzz_test.go` seeds known edge cases for malformed programs, large auto lengths, ANY values, recursive resources, and parse-log inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test/fuzz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test/fuzz_test.go -->
## sources/test-tools/syzkaller/prog/test/fuzz_test.go

Purpose: regression seeds for the fuzz entry points in `prog/test/fuzz.go`.

Important APIs/types/functions: `TestFuzz`.

Control flow: iterates over a list of malformed or edge-case program strings, logs the case index, converts each to a full-slice byte input, and runs both `FuzzDeserialize` and `FuzzParseLog`.

State and persistence: no persistence.

Dependencies/integration: depends on the fuzz package target initialization and deserializer/mutator invariants.

Risks: seed strings are compact reproductions for prior parser or mutation failures; future serializer grammar changes may require updating them.

Test signals: useful smoke coverage for previously risky malformed inputs, including unterminated pointers, invalid escapes, huge AUTO lengths, ANY blobs, repeated resources, and recursion.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test_util.go -->
## sources/test-tools/syzkaller/prog/test_util.go

Purpose: shared testing helpers for target initialization and deserialization table tests.

Important APIs/types/functions: `InitTargetTest`, `DeserializeTest`, and `TestDeserializeHelper`.

Control flow: `InitTargetTest` marks tests parallel and retrieves a target. `TestDeserializeHelper` runs each case under non-strict and strict modes, checks expected errors, optionally transforms the program, compares compact or verbose serialization to expected output, and verifies exec serialization does not fail.

State and persistence: no persistence. Test cases are local data structures.

Dependencies/integration: depends on target registry, deserializer modes, serializer variants, and `SerializeForExec`.

Risks: helper runs subtests in parallel through target init; target lazy init must be concurrency-safe. Expected output can match either verbose or non-verbose serialization to support strict-mode syntax.

Test signals: many package tests rely on this helper, so it amplifies coverage for deserialization, transformation, serialization, and exec encoding.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/testdata/fs_images/0.in -->
## sources/test-tools/syzkaller/prog/testdata/fs_images/0.in

Purpose: seed program containing a `syz_mount_image$bfs` call with a compressed BFS filesystem image buffer.

Important APIs/types/functions: the file is data, not Go code. It exercises `BufferCompressed` serialization syntax, `syz_mount_image` arguments, and image compression/decompression paths.

Control flow: consumed by tests or tools that load filesystem-image seeds, deserialize the one-line program, and then use compressed image data as a mutation target.

State and persistence: persistent test fixture under source control. Runtime state is created only when deserialized into a `Prog`.

Dependencies/integration: integrates with `image.Compress`/decompress mutation in `mutation.go`, serialization/deserialization, and filesystem-image tests outside this subset.

Risks: the compressed payload must remain valid. Mutating length metadata independently from compressed data can break decompression, which is why size mutation avoids compressed images.

Test signals: fixture presence supports compressed-image seed coverage; content is a minimal BFS mount-image input.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/testdata/fs_images/0.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/testdata/fs_images/1.in -->
## sources/test-tools/syzkaller/prog/testdata/fs_images/1.in

Purpose: seed program containing a `syz_mount_image$ext4` call with a compressed ext4 filesystem image buffer.

Important APIs/types/functions: data fixture for `syz_mount_image`, compressed buffer serialization, and image mutation paths.

Control flow: consumed by tests/tools that deserialize filesystem image seeds, mount or mutate the compressed payload, and verify serialization support.

State and persistence: persistent one-line test fixture. Runtime state exists only after deserialization.

Dependencies/integration: used with compressed image handling in `mutation.go`, `rand.go` compressed-buffer generation, and external fs image tests.

Risks: payload validity matters for decompression and mutation. Large compressed strings make diffs noisy and should be changed only through intentional fixture regeneration.

Test signals: complements `0.in` by covering ext4-specific mount-image seed shape.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/testdata/fs_images/1.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/types.go -->
## sources/test-tools/syzkaller/prog/types.go

Purpose: declares syscall metadata, type metadata, expressions, directions, resource descriptions, type traversal, default arguments, and C++ name conversion.

Important APIs/types/functions: `Syscall`, `SyscallAttrs`, `Dir`, `Field`, `Expression`, `BinaryExpression`, `Value`, `BinaryFormat`, `Type`, `Ref`, `TypeCommon`, `ResourceDesc`, `ResourceCtor`, `ResourceType`, integer type family, `LenType`, `ProcType`, `CsumType`, `VmaType`, `BufferType`, `ArrayType`, `PtrType`, `StructType`, `UnionType`, `TypeCtx`, `ForeachType`, `ForeachTypePost`, `ForeachCallType`, `ForeachArgType`, and `CppName`.

Control flow: type-specific methods provide defaults, default checks, string forms, sizes, bitfield metadata, and traversal behavior. Traversal recursively walks pointers, arrays, structs, unions, resources, buffers, and scalar types while tracking direction and optionality and pruning recursive struct/union visits by `(type, dir, optional)`.

State and persistence: type structs are in-memory target description data. `Ref` placeholders exist before `target.restoreLinks` replaces them with actual type pointers.

Dependencies/integration: central contract for compiler-generated descriptions, generation, mutation, validation, serialization, resource analysis, and target init.

Risks: incorrect `DefaultArg` or `isDefaultArg` breaks deserialization defaults and minimization. Traversal pruning must preserve direction/optional distinctions. `TypeCommon.Size` panics for varlen types, so callers must check `Varlen`.

Test signals: package-wide tests cover defaults, traversal effects, length assignment, generation, validation, and serialization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/prog/validation.go -->
## sources/test-tools/syzkaller/prog/validation.go

Purpose: validates in-memory program graph integrity, type/direction correctness, resource references, pointer bounds, argument sizes, and conditional-union completion.

Important APIs/types/functions: package `debug`, `Prog.debugValidate`, `Prog.validate`, `validCtx`, `validationOptions`, `validateWithOpts`, `validateCall`, `validateRet`, `validateArg`, and per-arg `validate` methods.

Control flow: validation walks calls in order, verifies metadata and call properties, validates each argument against expected type and direction, checks conditional fields, validates returns, then confirms every resource use references an in-tree arg. Each concrete arg validator enforces type-specific invariants.

State and persistence: reads program state and builds local `args` and `uses` maps. Debug validation is enabled for test binaries through `os.Args[0]` suffix.

Dependencies/integration: used after mutation, builder finalization, fuzzing, and tests. Depends on target special pointer ranges, `escapingFilename`, and conditional-field checking.

Risks: validation is intentionally strict except for unsafe programs. Pointer arithmetic must account for unsafe data-mmap surrounding pages. ANY pointers are allowed unless the call has `NoSquash`.

Test signals: many tests trigger debug validation; fuzz tests intentionally panic on invariant failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/prog/validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/darwin/init.go -->
## sources/test-tools/syzkaller/sys/darwin/init.go

Purpose: target-specific initialization for Darwin syzkaller targets.

Important APIs/types/functions: `InitTarget` and local `arch` wrapper containing `*targets.UnixNeutralizer`.

Control flow: constructs a Unix neutralizer, sets `target.MakeDataMmap` to a POSIX mmap helper with Darwin-specific flags, and assigns neutralization to the generic Unix neutralizer.

State and persistence: mutates in-memory `prog.Target` fields during lazy init. No persistence.

Dependencies/integration: depends on `prog.Target` and `sys/targets` helpers. Called through generated target registration.

Risks: Darwin-specific safety depends mostly on the generic Unix neutralizer. Incorrect mmap helper flags would affect generated memory setup programs.

Test signals: covered indirectly by target initialization and program generation tests over all targets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/darwin/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/empty.go -->
## sources/test-tools/syzkaller/sys/empty.go

Purpose: placeholder package file that keeps the `sys` package buildable before generated descriptions are available.

Important APIs/types/functions: none.

Control flow: no runtime behavior.

State and persistence: none.

Dependencies/integration: supports Go package build integrity for `github.com/google/syzkaller/sys`.

Risks: if generated registration files are absent, the build still succeeds but targets may not be registered.

Test signals: build-only signal; no direct tests are needed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/empty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/freebsd/init.go -->
## sources/test-tools/syzkaller/sys/freebsd/init.go

Purpose: target-specific initialization for FreeBSD syzkaller targets.

Important APIs/types/functions: `InitTarget` and local `arch`.

Control flow: creates a Unix neutralizer, sets a POSIX mmap helper with FreeBSD settings, and assigns neutralization to the generic Unix neutralizer.

State and persistence: mutates in-memory target hooks during lazy init. No persistence.

Dependencies/integration: depends on `prog.Target` and `targets.MakeUnixNeutralizer`/`MakePosixMmap`.

Risks: target safety is delegated to generic Unix neutralization. Mmap helper flags must match executor expectations for FreeBSD.

Test signals: indirectly covered by all-target generation and serialization tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/freebsd/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/fidlgen/main.go -->
## sources/test-tools/syzkaller/sys/fuchsia/fidlgen/main.go

Purpose: generation tool that invokes Fuchsia `fidlgen_syzkaller`, parses generated syz descriptions, prunes unused nodes, and writes per-library `.syz.txt` files atomically.

Important APIs/types/functions: `main` and `fidlgen`.

Control flow: `main` checks `TARGETOS`, `TARGETARCH`, and `SOURCEDIR`, resolves the Fuchsia build output and fidlgen binary, iterates `layout.AllFidlLibraries`, generates raw syz files from JSON IR, parses all `.txt` descriptions, collects unused nodes with the compiler, filters them, and rewrites each generated file with only relevant nodes. `fidlgen` validates JSON input, runs the external tool with a one-minute timeout, prints tool output, and returns the generated file path.

State and persistence: reads environment and Fuchsia build artifacts; writes `.syz.txt` files atomically in the working directory.

Dependencies/integration: depends on syzkaller AST/compiler packages, os utilities, tool failure handling, Fuchsia layout mapping, and target metadata.

Risks: silently returns when not building Fuchsia or `SOURCEDIR` is empty. External tool path and generated JSON paths are build-layout sensitive. Pruning correctness depends on compiler unused-node analysis.

Test signals: no direct tests in this subset; exercised by go generate and Fuchsia description generation workflows.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/fidlgen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/init.go -->
## sources/test-tools/syzkaller/sys/fuchsia/init.go

Purpose: target-specific initialization for Fuchsia targets.

Important APIs/types/functions: `InitTarget` and go:generate directives for amd64 and arm64 FIDL generation.

Control flow: sets `target.MakeDataMmap` to `targets.MakeSyzMmap`, using syzkaller's synthetic mmap helper rather than POSIX mmap.

State and persistence: mutates only the in-memory target hook. The go:generate comments drive source generation outside runtime.

Dependencies/integration: depends on `prog.Target`, `sys/targets`, and Fuchsia fidlgen output.

Risks: minimal runtime logic; correctness depends on generated descriptions and syz mmap support.

Test signals: indirect target initialization coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/layout/fidl_mappings.go -->
## sources/test-tools/syzkaller/sys/fuchsia/layout/fidl_mappings.go

Purpose: maps Fuchsia FIDL library names to build-output paths used by the fidlgen tool.

Important APIs/types/functions: `FidlLibrary`, `AllFidlLibraries`, `dirName`, `PathToJSONIr`, and `PathToCompiledDir`.

Control flow: `dirName` joins library components with dots. `PathToCompiledDir` builds the relative `fidling/gen/sdk/fidl/<library>` directory. `PathToJSONIr` appends `<library>.fidl.json` under that directory.

State and persistence: static library list only. No writes.

Dependencies/integration: consumed by `sys/fuchsia/fidlgen/main.go`.

Risks: the list and path layout must match the Fuchsia build tree. Adding/removing FIDL libraries requires updating `AllFidlLibraries`.

Test signals: no direct tests; failures surface in Fuchsia go generate workflows.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/fuchsia/layout/fidl_mappings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/generated/generated.go -->
## sources/test-tools/syzkaller/sys/generated/generated.go

Purpose: provides compressed gob serialization/deserialization and registration of generated syscall descriptions into `prog.Target`.

Important APIs/types/functions: `Desc`, `Register`, `fill`, `Serialize`, `FileName`, `Glob`, `fileName`, and `init` gob registrations.

Control flow: generated OS/arch packages call `Register`, which builds a target from `targets.List` metadata and registers filler/init callbacks. `fill` reads `gen/<os>_<arch>.gob.flate`, decompresses and gob-decodes a `Desc`, and populates target syscalls/resources/constants/flags/types. `Serialize` performs the inverse for generation tooling.

State and persistence: reads embedded generated gob files; writes serialized bytes only to caller-provided destinations. Registers concrete `prog.Type` and expression implementations with gob at init time.

Dependencies/integration: central bridge between compiler-generated descriptions and runtime target registration.

Risks: missing embedded files panic at target init. Gob registration must include every concrete type stored in `Desc`. File naming must stay stable for generators and embed patterns.

Test signals: indirectly exercised by every `GetTarget` and all-target test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/generated/generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/linux/init.go -->
## sources/test-tools/syzkaller/sys/linux/init.go

Purpose: Linux target initialization, special type wiring, special pointer/file-length configuration, and neutralization of dangerous or nondeterministic syscalls.

Important APIs/types/functions: `InitTarget`, `arch`, `arch.neutralize`, `neutralizeSchedAttr`, `enforceIntArg`, `neutralizeIoctl`, and `generateTimespec`.

Control flow: `InitTarget` loads many Linux constants, configures POSIX data mmap, assigns neutralization, registers Linux special generators for timespec, AF_ALG, netfilter, USB, and audio descriptors, sets auxiliary resources, architecture-specific special pointers, and special filename lengths. `neutralize` first applies generic Unix neutralization, then rewrites call arguments for mremap, syslog, ioctl, fanotify, ptrace, arch_prctl, init_module, syz_init_net_socket, syz_open_dev, sched_setattr, and ebtables.

State and persistence: mutates in-memory target hooks and per-call arguments during sanitization. No persistence.

Dependencies/integration: depends on generated Linux constants, `targets.MakeUnixNeutralizer`, `targets.MakePosixMmap`, `prog.Gen`, and additional Linux init files for AF_ALG/netfilter/USB generation.

Risks: neutralization protects host stability; missing constants or incomplete rewrites can cause hangs, machine freezes, or nondeterminism. Structural fixes are only partially honored by current target sanitize behavior.

Test signals: `prog_test.go` sanitization/idempotence, all-target generation, and special-struct tests indirectly exercise this logic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/linux/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/sys/linux/init_alg.go -->
## sources/test-tools/syzkaller/sys/linux/init_alg.go

Purpose: Linux AF_ALG special generation for `sockaddr_alg` and algorithm-name structs.

Important APIs/types/functions: `generateSockaddrAlg`, `generateAlgName`, `generateAlgAeadName`, `generateAlgHashName`, `generateAlgSkcipherhName`, `generateAlgNameStruct`, `generateAlgName`, `generateAlg`, `generateAlgImpl`, `fixedSizeData`, `algType`, `algDesc`, algorithm kind constants, `allTypes`, and `allAlgs`.

Control flow: `generateSockaddrAlg` generates the family, mostly zeroes feature/mask, randomly selects an algorithm type/name, pads or truncates fixed-size fields, and returns a struct arg. Name-specific functions generate fixed-size name structs for selected algorithm families. Recursive templates such as `authenc(hash,skcipher)` are built by `generateAlgImpl`.

State and persistence: static in-memory algorithm catalog. Generation returns new `prog.Arg` objects and no persistent writes.

Dependencies/integration: registered as Linux `target.SpecialTypes` in `init.go`; uses `prog.Gen` for random and regular field generation.

Risks: algorithm catalog can drift from kernel crypto availability. Recursive templates are bounded by catalog structure, not explicit recursion depth. Fixed-size truncation can cut generated names, which may be intentional for fuzzing but affects validity.

Test signals: indirectly covered by `TestSpecialStructs`, generation, mutation, and Linux target tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/sys/linux/init_alg.go -->
