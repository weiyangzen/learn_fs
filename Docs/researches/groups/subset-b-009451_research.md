# subset-b-009451 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/11cb68ad52ac78c81e33b806b531f097e68edfa2/arch/x86/crypto/aesni-intel_glue.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/11cb68ad52ac78c81e33b806b531f097e68edfa2/arch/x86/crypto/aesni-intel_glue.c

This file is a Linux x86 AES-NI crypto driver snapshot used by syzkaller covermerger integration data. It registers AES block cipher, skcipher modes, GCM/RFC4106 AEADs, xctr, and an added family of high-priority XTS implementations backed by AES-NI, VAES, AVX2, and AVX10 assembly entry points.

Important types include `aesni_rfc4106_gcm_ctx`, `generic_gcmaes_ctx`, `aesni_xts_ctx`, and `gcm_context_data`. The main API surface is kernel crypto callbacks: key setup (`aes_set_key_common`, `aesni_skcipher_setkey`, `xts_aesni_setkey`, AEAD setkey/authsize), encryption/decryption callbacks for ECB/CBC/CTS/CTR/XCTR/XTS/GCM, and module lifecycle (`aesni_init`, `aesni_exit`). Assembly dependencies are declared with `asmlinkage`; this revision changes `aesni_set_key` to return `void` and validates key length in C before entering the FPU-backed AES-NI key expansion.

Control flow is crypto-framework driven. `aesni_init` checks CPU AES support, enables AVX static branches for GCM, updates a static call for CTR-by8 when AVX is present, registers base cipher/skcipher/AEAD algorithms, conditionally registers xctr, then calls `register_xts_algs`. The new XTS path computes the tweak with `aes_xts_encrypt_iv`, uses a single-page fast path with local kmap, and falls back to `skcipher_walk_virt` plus ciphertext-stealing handling for page-spanning or partial-block requests. Cleanup reverses registrations and now includes `unregister_xts_algs`.

State is per transform context plus module-global registration state. Static keys select GCM implementation families, static calls select CTR implementation, and XTS registration pointers track optional SIMD wrappers. No normal filesystem persistence exists; persistence here is the source snapshot itself for coverage reconciliation. Dependencies are Linux crypto API, x86 CPU feature detection, FPU state management, scatterlist/skcipher walk helpers, SIMD compatibility wrappers, and architecture assembly symbols.

Integration risks are high because the file crosses C/assembly ABI boundaries and crypto API contracts. The XTS fast path must preserve FPU begin/end pairing, local mapping lifetimes, ciphertext stealing semantics, and CPU feature gating, especially AVX512 downclock avoidance via `zmm_exclusion_list`. Test signals come from its role as covermerger testdata: this revision is compared with nearby repository snapshots and exercises line addition/change attribution over real kernel code.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/11cb68ad52ac78c81e33b806b531f097e68edfa2/arch/x86/crypto/aesni-intel_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/9fe30842a90be9b57a3bd1a37c9aed92918cc6d0/arch/x86/crypto/aesni-intel_glue.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/9fe30842a90be9b57a3bd1a37c9aed92918cc6d0/arch/x86/crypto/aesni-intel_glue.c

This is an earlier Linux x86 AES-NI glue snapshot for covermerger integration testing. It exposes AES cipher and skcipher algorithms, RFC4106/GCM AEADs, CTR and xctr acceleration, and mode glue that routes crypto framework requests into AES-NI assembly when SIMD/FPU use is allowed.

Key structures are `aesni_rfc4106_gcm_ctx`, `generic_gcmaes_ctx`, `aesni_xts_ctx`, and aligned GCM context buffers. Important functions include `aes_set_key_common`, simple cipher wrappers (`aesni_encrypt`, `aesni_decrypt`), skcipher callbacks for ECB/CBC/CTS/CTR/XCTR/XTS, AEAD helpers (`gcmaes_crypt_by_sg`, `helper_rfc4106_encrypt/decrypt`, `generic_gcmaes_encrypt/decrypt`), algorithm descriptor arrays, and module lifecycle functions. In this snapshot `aesni_set_key` returns `int`, and `aes_set_key_common` checks AES key size before selecting generic or AES-NI key expansion.

Control flow starts with CPU feature checks in `aesni_init`. On x86_64, AVX/AVX2 feature checks select GCM static branches and CTR static-call optimization. Registration then proceeds through `crypto_register_alg`, `simd_register_skciphers_compat`, `simd_register_aeads_compat`, and optional xctr registration. Request paths use skcipher walks for block modes, scatter-gather AEAD walking for GCM, and FPU guard sections around assembly calls.

State is maintained in crypto transform contexts, request IVs, scatterlist walkers, and module-global SIMD wrapper pointers. The file does not persist runtime data; it is persisted as a repository snapshot for coverage-diff testing. External dependencies include Linux crypto, SIMD registration helpers, x86 feature helpers, FPU state helpers, scatterwalk/skcipher primitives, and matching assembly implementations.

Risks center on request-length corner cases, IV/tweak mutation, scatterlist alignment, AEAD tag verification, and keeping registration error unwinding symmetric. The snapshot has no local unit tests, but in this repository it is itself a high-value test fixture: covermerger can validate coverage movement against a realistic, multi-thousand-line kernel file with conditional compilation and assembly declarations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/9fe30842a90be9b57a3bd1a37c9aed92918cc6d0/arch/x86/crypto/aesni-intel_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/fe46a7dd189e25604716c03576d05ac8a5209743/arch/x86/crypto/aesni-intel_glue.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/fe46a7dd189e25604716c03576d05ac8a5209743/arch/x86/crypto/aesni-intel_glue.c

This file is another AES-NI kernel-driver snapshot in the covermerger integration corpus. Its contents match the `9fe30842...` snapshot in this work item, so its purpose is to provide a second repository identity with the same source body for merge/deduplication behavior in the integration scenario.

The code registers AES cipher, block modes, xctr, and GCM/RFC4106 AEAD implementations through Linux crypto APIs. Important context structs and callbacks are the same as the matching snapshot: AES and XTS contexts, aligned GCM context buffers, key setup helpers, skcipher mode callbacks, AEAD authentication helpers, algorithm descriptor arrays, and `aesni_init`/`aesni_exit`.

Control flow is crypto-framework callback driven. Module initialization gates on AES CPU support, chooses AVX or SSE GCM paths via static branches, optionally updates CTR dispatch to an AVX-by8 helper, then registers algorithm families. Runtime requests traverse skcipher or AEAD scatter-gather walkers, enter FPU sections for assembly acceleration, and write outputs, IVs, tags, or result buffers according to mode semantics.

State is stored in transform contexts, request-local buffers, IVs, global static branch/static-call state, and SIMD registration pointers. There is no application persistence. As a fixture, persistence is the source path and repository commit directory, which lets covermerger reason about identical files across distinct repositories.

Risks are those typical of low-level crypto glue: assembly ABI drift, invalid key handling, partial-block CTS/XTS semantics, scatterlist page boundaries, AEAD authentication failure handling, and registration unwind correctness. Test signals are indirect: identical content across two commit directories is useful for detecting whether the merger keys by path/content/repository identity correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/aesni-intel_glue/test-workdir-covermerger/repos/fe46a7dd189e25604716c03576d05ac8a5209743/arch/x86/crypto/aesni-intel_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/add_line.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/add_line.c

This tiny C fixture represents the pre-change side of an added-line scenario. It contains a single `func1` body with only `line2`, intentionally using placeholder tokens rather than compilable C statements.

The important API is just `void func1()`. Control flow is linear and empty aside from the marker line. There is no state, persistence, dependencies, or integration logic beyond its path in covermerger integration data.

Its paired `commit2/add_line.c` adds `line3`, so this file helps validate whether covermerger maps coverage and diff hunks when a line is inserted after an existing line. The main risk is treating it as buildable C; it is a structural diff fixture. Test signal is the minimal before/after contrast.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/add_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/change_line.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/change_line.c

This fixture is the pre-change side of a line-modification case. `func1` contains `line2` followed by `line3`, with both lines serving as stable textual markers.

There are no real APIs beyond `func1`, and no runtime state, persistence, or external dependency. Control flow is a simple function body whose second logical line is the target for comparison with `commit2/change_line.c`.

The integration point is the covermerger test fixture set. In the paired commit, `line2` changes to `line2_changed` while `line3` remains stable, letting the merger distinguish changed-line coverage from unchanged-context coverage. The main risk is assuming semantic C behavior; this file is for textual and coverage reconciliation behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/change_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_code.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_code.c

This file is the pre-delete-code side of a fixture pair. It defines `func1` with a single marker statement `line1`.

Its only exposed unit is `void func1()`. Control flow has no branches, state, persistence, or external dependencies. The marker is intentionally not valid C syntax because the file is consumed as integration test data, not built.

The paired `commit2/delete_code.c` is empty, so this file tests handling of code removal where a path still exists but contains no source lines. Risks are around line mapping: removed executable markers should not be incorrectly attributed to the empty successor file. The test signal is the stark non-empty-to-empty transition.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_file.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_file.c

This fixture models a file that exists in commit1 and is absent from the commit2 list. It contains `func1` with a single marker `line1`.

There are no meaningful runtime APIs beyond the placeholder function, and no state or persistence behavior. Its integration behavior is entirely path-level: covermerger must recognize a source file that disappears between revisions.

The risk is conflating deleted-file handling with empty-file handling. Unlike `delete_code.c`, there is no mapped commit2 counterpart in this work item. Test signal is the presence-only-in-commit1 path, which validates deletion accounting and prevents stale coverage from being assigned to unrelated files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/delete_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/not_changed.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/not_changed.c

This is the commit1 side of an unchanged-file fixture. `func1` contains marker lines `line1`, `line2`, and `line3`.

There are no real APIs, control branches, state, persistence, or dependencies. The source is intentionally minimal to isolate path and line preservation behavior.

Its paired `commit2/not_changed.c` is identical, so the integration point is covermerger's unchanged-file reconciliation path. The expected signal is stable line identity across commits. Risk lies in over-attributing differences due to repository directory changes rather than source content changes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit1/not_changed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/add_line.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/add_line.c

This is the post-change side of the add-line fixture. `func1` contains `line2` and a newly present `line3`.

The file has no functional dependencies, persistence, or state. Its control flow remains a single function body; the important behavior is textual position and line identity relative to commit1.

The integration point is covermerger's added-line mapping. Compared with `commit1/add_line.c`, this file tests whether new coverage lines can be recognized as introduced source while preserving existing-line correspondence. Risk is limited to fixture interpretation: it is not valid buildable C and should be treated as synthetic source data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/add_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/change_line.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/change_line.c

This is the post-change side of a modified-line fixture. `func1` contains `line2_changed` followed by unchanged `line3`.

There are no runtime APIs beyond the placeholder function, no state, and no dependencies. Control flow is flat; the changed marker is the whole purpose of the file.

The file integrates with the paired commit1 fixture to verify changed-line detection. It should let covermerger distinguish a replacement line from stable surrounding context. The risk is false continuity: tools must not treat `line2_changed` as the same source line as `line2` except as a diff-mapped modification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/change_line.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/delete_code.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/delete_code.c

This file is intentionally empty. It is the post-change counterpart to a commit1 file that contained a placeholder `func1` body.

There are no APIs, functions, control flow, state, persistence, dependencies, or local tests inside the file. Its meaning comes from the path and empty content in the covermerger integration fixture.

The integration point is deletion-with-path-retained handling. It verifies that an empty successor file is distinct from a missing file and that previous coverage lines are not silently carried forward. The main risk is treating zero-byte research targets as missing; the correct output still needs to document the intentional empty state.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/delete_code.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/not_changed.c -->
# sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/not_changed.c

This is the commit2 side of the unchanged-file fixture. It defines the same placeholder `func1` body with `line1`, `line2`, and `line3`.

No functional APIs, persistence, dependencies, or state are present. The only meaningful control-flow fact is that the source layout remains identical to commit1.

Its integration value is stable baseline coverage mapping. Covermerger should preserve line correspondence exactly despite the different commit directory. Test signal is byte-level sameness with `commit1/not_changed.c`; risk is any path-only logic that reports a change where none exists.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/covermerger/testdata/integration/all/test-workdir-covermerger/repos/commit2/not_changed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/build.go -->
# sources/test-tools/syzkaller/pkg/csource/build.go

This Go file builds generated C/C++ reproducers and formats generated C source. Public functions are `Build`, `BuildNoWarn`, `BuildExecutor`, and `Format`; the private `build` routine holds compiler selection and invocation.

`build` creates a temporary `syz-executor` binary path, assembles target macros (`GOOS_`, `GOARCH_`, `HOSTGOOS_`), selects C or C++ compiler/flags from `targets.Get`, streams generated C through stdin when no source file is supplied, and returns detailed source/output/invocation diagnostics on failure. `BuildNoWarn` relaxes compiler warnings for old reproducers or unknown compilers, while `BuildExecutor` compiles `executor/executor.cc` with `-O0` for tests and registers cleanup with `testing.T`.

State is mostly transient: temporary output files are created and removed on failure or test cleanup. Dependencies are `osutil.Command`, syzkaller target metadata, Go runtime host OS, and clang-format. `Format` pipes source through `clang-format` using an embedded Linux-kernel-friendly style.

Integration points include csource tests, reproducers, bisection, and executor test builds. Risks include target compiler availability, stale target flags, warning policy differences, leaked temp binaries outside test cleanup, and formatter absence. Test signals are indirect in `csource_test.go`, where generated sources are built through `Build`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/common.go -->
# sources/test-tools/syzkaller/pkg/csource/common.go

This file prepares the executor common header used as the template for generated C reproducers. Its central functions are `createCommonHeader`, `defineList`, `commonDefines`, and `removeSystemDefines`.

`createCommonHeader` computes feature and syscall defines, runs the target C preprocessor over `executor.CommonHeader` with `-nostdinc` and directive-preserving flags, strips compiler/system defines, applies placeholder replacements, normalizes syzkaller integer aliases to C stdint types, and removes `SYZ_HAVE_*` defines. `defineList` includes common feature macros plus syscall numbers used by the main and mmap setup programs. `commonDefines` maps `Options` and program-required features to `SYZ_*` preprocessor symbols.

State is transient source bytes and define lists; no persistence occurs. Dependencies include target CPP configuration, executor bundled headers, program feature extraction, runtime host OS, and target metadata. Integration is tight with `csource.go`, which supplies replacement values for process counts, syscalls, timeouts, sandbox entry, results, and generated call bodies.

Risks include silently ignoring preprocessor errors when stdout is non-empty, missing real CPP failures among expected `-nostdinc` include errors, stale macro lists, and replacement-token mismatches. Test signals include `TestExecutorMacros`, generated-source build tests, and syscall-generation fixtures that exercise comments and call expansion after common header preprocessing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/csource.go -->
# sources/test-tools/syzkaller/pkg/csource/csource.go

This is the core syzkaller program-to-C reproducer generator. Public entry points are `Write`, which validates `Options` and emits a full C program, and `WriteLLM`, which emits a minimal single-threaded/commented reproducer intended for LLM consumption.

The internal `context` carries the program, options, target metadata, and syscall-number map. `generateSource` filters disabled pseudo syscalls, generates main program calls and mmap setup calls, records syscall numbers plus pseudo-syscall dependencies, builds replacement strings for the executor template, computes timeout expressions, preprocesses the common header, prepends the autogenerated banner, and post-processes text. Call generation flows through `generateProgCalls`, `generateCalls`, `emitCall`, and `fmtCallBody`, translating the exec serialization into C copyin statements, syscall or pseudo-call invocations, fault injection, reruns, tracing, copyout, and result variables.

State is generated text plus result variable arrays; runtime persistence is absent. The generator depends on `prog` serialization/deserialization, target syscall metadata, executor common headers, C preprocessor output from `common.go`, and target constants/flags. Integration points include reproducers, runtest tracing, LLM output, csource tests, and target-specific syscall wrappers.

Important helper behavior includes bitfield and endian-aware copyins, checksum generation, pretty flag comments, resource result expressions, include hoisting, failure/debug macro stripping, and empty-line cleanup. Risks include ABI-sensitive literal sizing, native versus trampoline call classification, non-native `NONFAILING` wrapping, option-sensitive filtering of networking/HCI helpers, and text-regex postprocessing that can overmatch. Tests in `csource_test.go`, `options_test.go`, and `syscall_generation_test.go` cover generated snippets, builds, comments, options, and syscall formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/csource.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/csource_test.go -->
# sources/test-tools/syzkaller/pkg/csource/csource_test.go

This file tests generated C source across syzkaller targets, option sets, pseudo syscalls, comments, sandbox signatures, and the LLM-oriented output path.

Important test helpers are `TestGenerate`, `testTarget`, `testPseudoSyscalls`, `testOne`, `TestExecutorMacros`, `TestSource`, `TestGenerateSandboxFunctionSignature`, and `TestWriteLLM`. `TestGenerate` iterates all targets whose compiler can run on the host, builds representative programs, and compiles generated C. `testTarget` varies option breadth by short/full mode and injects call properties such as fault injection, async, and rerun. `testOne` limits noisy failures, calls `Write`, checks include guard removal, then builds the result.

State is test-local plus a package-level `failedTests` counter used to cap failure spew. Dependencies include target descriptions, executor common headers, testutil race detection, generated programs, `Build`, and testify assertions. Integration points are broad: failures here indicate regressions in csource generation, target metadata, compiler flags, executor macros, or formatting assumptions.

Risk areas include high memory and compile cost, race-detector timeouts, host compiler availability, target-specific broken compilers, and generated output changes requiring expected snippet updates. The test signal is strong because it exercises both semantic generation and actual compilation. `TestWriteLLM` specifically verifies comments are present, sandbox scaffolding is omitted, syscalls appear inside `main`, and generated source builds.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/csource_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/options.go -->
# sources/test-tools/syzkaller/pkg/csource/options.go

This file defines and validates csource generation options, serializes/deserializes option payloads, handles legacy dashboard formats, parses manual feature flags, and converts feature negotiation into executor environment flags.

The main type is `Options`, containing execution topology, sandbox, leak checking, network/device setup, filesystem/environment setup, tracing, comments, and embedded `LegacyOptions`. `Check` validates cross-option constraints such as collide requiring threaded mode, procs/net reset/repeat-times requiring repeat, sandbox-required setup options, namespace requiring tmpdir, cgroups requiring tmpdir, and OS-specific Linux-only restrictions. `DefaultOpts` derives manager defaults from `mgrconfig.Config`.

Persistence is JSON serialization through `Serialize` and `DeserializeOptions`; legacy parser support reads older struct-like strings and old JSON keys so dashboard reproducers remain usable. `ParseFeaturesFlags`, `PrintAvailableFeaturesFlags`, `FeaturesToFlags`, and `FlatRPCFeaturesToCSource` bridge manual enable/disable names with `flatrpc` feature and execution environment bits.

Dependencies include JSON, reflection-friendly comparable option structs, manager config, flatrpc enums, and target OS constants. Integration points are syz-manager default repro generation, dashboard-stored reproducers, executor feature negotiation, and csource tests. Risks include backwards compatibility with legacy fields, invalid option combinations creating uncompilable C, feature-name drift between flatrpc and csource, and non-Linux option leakage. Tests in `options_test.go` cover round trips, canned legacy values, valid option enumeration, and feature flag parsing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/options_test.go -->
# sources/test-tools/syzkaller/pkg/csource/options_test.go

This test file validates option serialization compatibility, option-space enumeration, and feature flag parsing for csource.

`TestParseOptions` round-trips representative single-field option variations through JSON. `TestParseOptionsCanned` verifies current and legacy dashboard payloads, including older fields like `collide`, `fault`, `EnableTun`, empty sandbox encoding, Android sandbox args, and namespace sandbox args. `allOptionsSingle`, `allOptionsPermutations`, `dedup`, and `enumerateField` generate valid option sets while filtering through `Options.Check`.

`TestParseFeaturesFlags` checks `-enable` and `-disable` combinations such as `none`, `all`, empty strings, selected feature subsets, and default-enabled/default-disabled behavior. State is test-local; dependencies are `reflect`, `math` boundary values for sandbox args, target OS constants, and the option parser under test.

Integration signal is high for backward compatibility because dashboard reproducers may contain old serialized formats. Risks include missing newly added `Options` fields in enumeration expectations, legacy parser breakage, feature map drift, and duplicate or invalid combinations slipping into generation tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/syscall_generation_test.go -->
# sources/test-tools/syzkaller/pkg/csource/syscall_generation_test.go

This file snapshot-tests syscall expression and generated argument comments against files under `pkg/csource/testdata`. It is focused on exact formatting, not full C compilation.

Important types are `testData` and `annotatedCall`. `TestGenerateSyscalls` reads test cases, creates a Linux/amd64 target, and compares generated comments and `fmtCallBody` output to checked-in expectations. A `-update` flag rewrites testdata when generation intentionally changes. `readTestCases` and `readTestData` parse each fixture as input program lines up to a blank line followed by repeated comment blocks and syscall expression lines. `testGenerationImpl` deserializes the program, formats comments through `Format`, serializes/deserializes exec form, and compares each generated syscall body.

State and persistence are limited to optional fixture rewriting when `-update` is set. Dependencies include clang-format through `Format`, Linux/amd64 target metadata, `prog` parsing, and exact comment prefix conventions from `csource.go`.

Risks include brittle textual comparisons, formatter availability, testdata parser assumptions about blank lines and comment prefixes, and broad fixture rewrites hiding unintended changes. Test signal is precise: failures pinpoint changes in argument annotation, resource formatting, native syscall names, constants/flags, and pointer/value rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/syscall_generation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/0 -->
# sources/test-tools/syzkaller/pkg/csource/testdata/0

This syscall-generation fixture contains a two-call netlink program and its expected generated comments plus syscall bodies. The input opens a netlink socket and binds it to a `sockaddr_nl_t` with a group bitmap.

Important signals are resource flow from `socket$netlink` return value `r0` into `bind$netlink`, constant/flag annotation (`NETLINK_USERSOCK`), pointer address rendering, and translation from syzkaller call variants to native `__NR_socket` and `__NR_bind` syscalls. There is no executable state inside the file beyond fixture text.

The integration point is `syscall_generation_test.go`, which parses the program before the blank line and compares the stored comments/syscall lines after it. Risks are exact-format brittleness and target metadata changes affecting annotation names or numeric constants. Test signal is compact coverage of resource comments, struct field comments, native syscall names, and generated argument comments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/0 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/1 -->
# sources/test-tools/syzkaller/pkg/csource/testdata/1

This fixture captures an iommufd-oriented syscall sequence and expected csource formatting. The input opens `/dev/iommu`, allocates an IOAS, maps pages, creates access, and performs a syzkaller-specific access-pages ioctl.

The important APIs represented are `openat$iommufd` and several `ioctl$IOMMU_*` variants. The expected output verifies native syscall collapse to `__NR_openat` and `__NR_ioctl`, resource propagation through `r[0]`, `r[1]`, and `r[2]`, struct field comments, output-resource annotations, VMA pointer rendering, and flag/constant naming.

State is textual fixture data; persistence is the checked-in expected output. Dependencies are Linux/amd64 syscall descriptions and csource comment formatting. Integration is through the syscall-generation snapshot test. Risks include kernel description drift, changed IOMMU constants, and formatter output changes. The test signal is useful for complex nested structs, in/out resources, ioctl command constants, and syzkaller pseudo-variant formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/1 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/2 -->
# sources/test-tools/syzkaller/pkg/csource/testdata/2

This large fixture stores an option-prefixed filesystem reproducer and expected generated comments/syscall bodies. The program mounts an f2fs image, performs file operations, opens a null block device, sends data, and runs `quotactl`.

Important signals include parsing of a leading JSON options line, large compressed-buffer representation for `syz_mount_image$f2fs`, flag pretty-printing (`MS_NOEXEC`, open flags, mode flags, quota command), resource flow across open/fallocate/sendfile, and pointer rendering for file-name buffers and image data. The file is not code to execute directly; it is source data for the syscall-generation test parser and comparator.

State is the fixture's expected text. Dependencies are Linux target descriptions, generated comments, csource formatting, and stable compression-buffer display rules. Integration is with `syscall_generation_test.go`, where this fixture stresses long comments, arrays/unions, generated pseudo syscall calls, and native syscall formatting. Risks are high output churn from formatter or target-description changes, but the test signal is broad coverage of complex generated reproducer formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/csource/testdata/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/db/db.go -->
# sources/test-tools/syzkaller/pkg/db/db.go

This package implements syzkaller's small append-oriented corpus key-value database. It caches records in memory while mirroring mutations to a compressed binary file, minimizing disk work for syz-manager and syz-hub corpus storage.

The central types are `DB` and `Record`. Public operations include `Open`, `Save`, `Delete`, `DiscardData`, `Flush`, `BumpVersion`, `Create`, `ReadCorpus`, and `Merge`. The on-disk format uses a database header (`dbMagic`, `curVersion`, user version) followed by record entries (`recMagic`, key length/key, sequence, compressed value length/value). `seqDeleted` represents tombstones.

Control flow in `Open` deserializes whatever can be recovered, optionally returns a soft error in repair mode, and compacts to ensure a writable normalized file. `Save` appends pending records unless the same key/value/sequence is already present. `Flush` appends pending bytes and compacts when stale entries dominate. `compact` rewrites a temporary file and atomically renames it. `Merge` accepts both DB files and seed program files, saving valid seeds by hash.

Persistent state is the database file; in-memory state is `Records`, version, uncompacted count, pending write buffer, and `dataDiscarded`. Dependencies include flate compression, binary little-endian encoding, hash generation, target program deserialization, and `osutil` atomic file helpers. Risks include corruption recovery boundaries, decompression bombs, oversized keys, pending-buffer loss before flush, data-discard compaction rereads, and map iteration order during compaction. Tests in `db_test.go` cover basic persistence, modification/tombstones, large data, discard mode, inaccessible/corrupt files, and OOM guards.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/db/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/db/db_test.go -->
# sources/test-tools/syzkaller/pkg/db/db_test.go

This file tests the corpus DB implementation's persistence, mutation, recovery, memory-saving mode, and crafted-input bounds checks.

Core tests include `TestBasic` for save/flush/reopen, `TestModify` for updates and deletes, `TestLarge` for many compressed records, `TestDiscardData` for nil in-memory values plus compaction reread, `TestOpenInvalid` and `TestOpenCorrupted` for repair-mode behavior, and `TestOpenInaccessible` for permission failures when not root. `TestDecompressionBombValLen` verifies decompressed values over `maxValLen` are rejected, and `TestOversizeKeyLen` verifies oversized key lengths fail before large allocation.

State is temporary database files created through `tempFile` and deleted after tests. Dependencies are `osutil`, binary encoding helpers from `db.go`, flate serialization through production code, random data for large records, and testify assertions.

Integration signal is strong for durability and security boundaries: the tests assert that repair mode returns a non-nil DB with recovered records on corruption, that atomic compaction preserves desired records, and that hostile record lengths do not cause OOM. Risks include nondeterministic compression sizes, root-specific permission semantics, and test expectations tied to the current compaction threshold.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/db/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/debugtracer/debug.go -->
# sources/test-tools/syzkaller/pkg/debugtracer/debug.go

This package defines a small tracing abstraction used by syzkaller components that need optional debug logging or artifact capture. The interface is `DebugTracer` with `Logf` and `SaveFile`.

Implementations are `GenericTracer`, `TestTracer`, and `NullTracer`. `GenericTracer` writes formatted log lines to an `io.Writer`, optionally prefixing timestamps in `02-Jan-2006 15:04:05` format, and saves named files under `OutDir` when configured. `TestTracer` forwards logs to `testing.T.Logf` and leaves file saving unimplemented. `NullTracer` drops both logs and saved files.

State is minimal: writer, output directory, timestamp flag, or test handle. Persistence occurs only through `GenericTracer.SaveFile`, which ensures `OutDir` exists and writes a file with `osutil.WriteFile`. Dependencies are standard formatting/time/path APIs plus `osutil`.

Integration points are callers that want debug traces without hard-coding test or filesystem behavior. Risks include ignoring write errors from `MkdirAll`/`WriteFile`, filename path traversal if untrusted names are supplied, nil `TraceWriter` panics, and no-op `SaveFile` behavior in tests hiding artifact expectations. There are no direct tests in this file, so confidence comes from simple implementation and downstream use.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/debugtracer/debug.go -->
