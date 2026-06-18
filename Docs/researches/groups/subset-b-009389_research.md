# subset-b-009389 research

Grouped research report for stress-ng configure probes in `sources/test-tools/stress-ng/test`. Each source file was read from the manifest and summarized with source-tree-aligned markers so the reconciliation lane can split per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_storeu_si256.c -->
# sources/test-tools/stress-ng/test/test-mm256_storeu_si256.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm256_storeu_si256` using 256-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m256i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm256_storeu_si256`; calls `target`, `_mm256_storeu_si256`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm256_storeu_si256`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_storeu_si256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_add_epi8.c -->
# sources/test-tools/stress-ng/test/test-mm512_add_epi8.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_add_epi8` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_add_epi8`; calls `target`, `_mm512_add_epi8`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512bw`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_add_epi8`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_add_epi8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_dpbusd_epi32` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_dpbusd_epi32`; calls `target`, `_mm512_dpbusd_epi32`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512vnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_dpbusd_epi32`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpbusd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpwssd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm512_dpwssd_epi32.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_dpwssd_epi32` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_dpwssd_epi32`; calls `target`, `_mm512_dpwssd_epi32`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512vnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_dpwssd_epi32`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_dpwssd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_loadu_si512.c -->
# sources/test-tools/stress-ng/test/test-mm512_loadu_si512.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_loadu_si512` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_loadu_si512`; calls `target`, `_mm512_loadu_si512`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512bw`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_loadu_si512`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_loadu_si512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_storeu_si512.c -->
# sources/test-tools/stress-ng/test/test-mm512_storeu_si512.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm512_storeu_si512` using 512-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m512i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm512_storeu_si512`; calls `target`, `_mm512_storeu_si512`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avx512bw`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm512_storeu_si512`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm512_storeu_si512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_add_epi8.c -->
# sources/test-tools/stress-ng/test/test-mm_add_epi8.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_add_epi8` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m128i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm_add_epi8`; calls `target`, `_mm_add_epi8`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_add_epi8`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_add_epi8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_dpbusd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm_dpbusd_epi32.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_dpbusd_epi32` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m128i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm_dpbusd_epi32`; calls `target`, `_mm_dpbusd_epi32`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_dpbusd_epi32`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_dpbusd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_dpwssd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm_dpwssd_epi32.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_dpwssd_epi32` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m128i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm_dpwssd_epi32`; calls `target`, `_mm_dpwssd_epi32`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_dpwssd_epi32`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_dpwssd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_getcsr.c -->
# sources/test-tools/stress-ng/test/test-mm_getcsr.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_getcsr` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`; defines `main`; uses intrinsics `_mm_getcsr`; calls `_mm_getcsr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_getcsr`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_getcsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_loadu_si128.c -->
# sources/test-tools/stress-ng/test/test-mm_loadu_si128.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_loadu_si128` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m128i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm_loadu_si128`; calls `target`, `_mm_loadu_si128`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_loadu_si128`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_loadu_si128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_setcsr.c -->
# sources/test-tools/stress-ng/test/test-mm_setcsr.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_setcsr` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`; defines `main`; uses intrinsics `_mm_setcsr`; calls `_mm_setcsr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_setcsr`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_setcsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_storeu_si128.c -->
# sources/test-tools/stress-ng/test/test-mm_storeu_si128.c

Purpose: compile and runtime smoke probe for the x86 SIMD intrinsic `_mm_storeu_si128` using 128-bit integer vectors; it verifies that the compiler accepts the header, target attribute, vector type, and intrinsic call used by stress-ng feature detection.

Important APIs/types/functions: includes `immintrin.h`, `string.h`, `stdint.h`; uses types `__m128i`; defines `rndset`, `__attribute__`; uses intrinsics `_mm_storeu_si128`; calls `target`, `_mm_storeu_si128`.

Control flow: helper definitions `rndset`, `__attribute__` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value SIMD probes fill vector storage with `rndset()`, execute the intrinsic, and return an integer lane from the result or source vector.

State and persistence behavior: all state is stack-local vector or byte-buffer data seeded by `rndset()` from the helper function address. No files, kernel objects, or persistent settings are intentionally created; executing the binary may require CPU support for the targeted instruction set.

Dependencies and integration points: depends on headers `immintrin.h`, `string.h`, `stdint.h`; compiler target attributes `avxvnni`; x86 intrinsic support from `immintrin.h` and matching compiler code generation. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SIMD probes can compile but fail with illegal-instruction behavior if run on a CPU lacking the requested ISA despite the compiler accepting the target attribute. the integer return reads bytes from vector storage solely as an anti-optimization signal, so it is not a semantic correctness check. Test signals are successful compilation; successful linking; accepted intrinsic code generation for `_mm_storeu_si128`; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm_storeu_si128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mnt_id_req.c -->
# sources/test-tools/stress-ng/test/test-mnt_id_req.c

Purpose: compile-time availability probe for `struct mnt_id_req` associated with `mnt_id_req`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/mount.h`; uses types `struct mnt_id_req`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/mount.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mnt_id_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mode_t.c -->
# sources/test-tools/stress-ng/test/test-mode_t.c

Purpose: compile-time availability probe for `mode_t` associated with `mode_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/stat.h`, `sys/types.h`; uses types `mode_t`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/stat.h`, `sys/types.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mode_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-modify-ldt.c -->
# sources/test-tools/stress-ng/test/test-modify-ldt.c

Purpose: minimal stress-ng configure probe for `modify-ldt`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `asm/ldt.h`, `string.h`; uses types `struct user_desc`; defines `main`; calls `memset`, `syscall`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_modify_ldt` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `sys/syscall.h`, `sys/types.h`, `asm/ldt.h`, `string.h`; architecture syscall numbers `__NR_modify_ldt`; preprocessor availability gates such as `#if !defined(__NR_modify_ldt)`, `#error modify_ldt syscall not defined`, `#if defined(__x86_64__) || defined(__x86_64) || \`, `#error modify_ldt syscall not applicable for non-x86 architectures`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; the expected syscall symbol being present; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-modify-ldt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-move-mount.c -->
# sources/test-tools/stress-ng/test/test-move-mount.c

Purpose: minimal stress-ng configure probe for the Linux mount move API; it compiles and often lightly invokes `move-mount`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `sys/mount.h`; defines `main`; calls `move_mount`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`, `sys/mount.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-move-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mprotect.c -->
# sources/test-tools/stress-ng/test/test-mprotect.c

Purpose: minimal stress-ng configure probe for the memory protection API; it compiles and often lightly invokes `mprotect`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdint.h`, `sys/mman.h`; defines `main`; calls `mprotect`; references constants/macros `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, `PROT_NONE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: changes page protections for process-local memory and does not persist outside the process.

Dependencies and integration points: depends on headers `stdint.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mprotect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-posix.c -->
# sources/test-tools/stress-ng/test/test-mq-posix.c

Purpose: minimal stress-ng configure probe for the POSIX message queue API; it compiles and often lightly invokes `mq-posix`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `mqueue.h`, `signal.h`, `fcntl.h`; uses types `struct mq_attr`, `struct timespec`, `struct sigevent`, `union sigval`, `mqd_t`; defines `notify_func`, `main`; calls `snprintf`, `getpid`, `mq_open`, `memset`, `mq_notify`, `mq_timedreceive`, `mq_receive`, `mq_getattr`, `mq_timedsend`, `mq_send`, `mq_close`, `mq_unlink`; references constants/macros `O_CREAT`, `O_RDWR`, `SIGEV_THREAD`.

Control flow: helper definitions `notify_func` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a named POSIX message queue and removes it with `mq_unlink`; queue attributes and pending messages are transient kernel state.

Dependencies and integration points: depends on headers `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `mqueue.h`, `signal.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error posix message queues not implemented on GNU/HURD`, `#if defined(__FreeBSD_kernel__)`, `#error posix message queues not implemented with FreeBSD kernel`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. path names derived from `argv[0]` can include slashes or unusual characters when the probe is launched from uncommon build harnesses. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size; message-queue library compatibility where the platform still requires `-lrt`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-sysv.c -->
# sources/test-tools/stress-ng/test/test-mq-sysv.c

Purpose: minimal stress-ng configure probe for the System V message queue API; it compiles and often lightly invokes `mq-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `sys/ipc.h`, `sys/msg.h`; uses types `struct msqid_ds`, `struct msginfo`; defines `main`; calls `MAX_SIZE`, `msgget`, `memset`, `strncpy`, `msgsnd`, `msgrcv`, `msgctl`; references constants/macros `IPC_PRIVATE`, `IPC_CREAT`, `IPC_EXCL`, `IPC_STAT`, `IPC_RMID`, `IPC_INFO`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V message queue and requests cleanup with `IPC_RMID`; message contents and queue metadata are transient kernel IPC state.

Dependencies and integration points: depends on headers `unistd.h`, `stdio.h`, `string.h`, `sys/types.h`, `sys/stat.h`, `sys/ipc.h`, `sys/msg.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error msgsnd, msgrcv, msgget, msgctl are not implemented`, `#if defined(__linux__)`, `#if defined(__linux__)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mq-sysv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mquery.c -->
# sources/test-tools/stress-ng/test/test-mquery.c

Purpose: minimal stress-ng configure probe for `mquery`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stdlib.h`, `sys/mman.h`; defines `main`; calls `mquery`; references constants/macros `PROT_READ`, `MAP_FIXED`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mquery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mremap.c -->
# sources/test-tools/stress-ng/test/test-mremap.c

Purpose: minimal stress-ng configure probe for the Linux mapping resize API; it compiles and often lightly invokes `mremap`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `stddef.h`; defines `main`; calls `mremap`; references constants/macros `MREMAP_FIXED`, `MREMAP_MAYMOVE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `stddef.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mseal.c -->
# sources/test-tools/stress-ng/test/test-mseal.c

Purpose: minimal stress-ng configure probe for the Linux memory sealing API; it compiles and often lightly invokes `mseal`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/mman.h`; defines `main`; calls `mmap`, `mseal`; references constants/macros `PROT_READ`, `PROT_WRITE`, `MAP_ANONYMOUS`, `MAP_PRIVATE`, `MAP_FAILED`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mseal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msginfo.c -->
# sources/test-tools/stress-ng/test/test-msginfo.c

Purpose: compile-time availability probe for `struct msginfo` associated with `msginfo`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/msg.h`; uses types `struct msginfo`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/msg.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msync.c -->
# sources/test-tools/stress-ng/test/test-msync.c

Purpose: minimal stress-ng configure probe for the memory-map synchronization API; it compiles and often lightly invokes `msync`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `string.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`; defines `main`; calls `memset`, `open`, `unlink`, `write`, `mmap`, `msync`, `munmap`, `close`; references constants/macros `O_RDWR`, `O_CREAT`, `PROT_READ`, `PROT_WRITE`, `MAP_PRIVATE`, `MAP_FAILED`, `MS_ASYNC`, `MS_SYNC`, `MS_INVALIDATE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value error handling uses a compact cleanup label so opened descriptors or mappings are released before returning failure.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `string.h`, `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error msync is defined but not implemented and will always fail`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-msync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtrr_gentry.c -->
# sources/test-tools/stress-ng/test/test-mtrr_gentry.c

Purpose: compile-time availability probe for `struct mtrr_gentry` associated with `mtrr_gentry`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `asm/mtrr.h`; uses types `struct mtrr_gentry`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `asm/mtrr.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtrr_gentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtrr_sentry.c -->
# sources/test-tools/stress-ng/test/test-mtrr_sentry.c

Purpose: compile-time availability probe for `struct mtrr_sentry` associated with `mtrr_sentry`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `asm/mtrr.h`; uses types `struct mtrr_sentry`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `asm/mtrr.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtrr_sentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-destroy.c -->
# sources/test-tools/stress-ng/test/test-mtx-destroy.c

Purpose: minimal stress-ng configure probe for the C11 threads mutex API; it compiles and often lightly invokes `mtx-destroy`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `threads.h`, `string.h`; uses types `mtx_t`; defines `main`; calls `memset`, `mtx_destroy`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses stack-allocated C11 mutex state only.

Dependencies and integration points: depends on headers `threads.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-destroy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-init.c -->
# sources/test-tools/stress-ng/test/test-mtx-init.c

Purpose: minimal stress-ng configure probe for the C11 threads mutex API; it compiles and often lightly invokes `mtx-init`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `threads.h`, `string.h`; uses types `mtx_t`; defines `main`; calls `memset`, `mtx_init`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses stack-allocated C11 mutex state only.

Dependencies and integration points: depends on headers `threads.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx_t.c -->
# sources/test-tools/stress-ng/test/test-mtx_t.c

Purpose: compile-time availability probe for `mtx_t` associated with `mtx_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `threads.h`, `string.h`; uses types `mtx_t`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses stack-allocated C11 mutex state only.

Dependencies and integration points: depends on headers `threads.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mtx_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-munlock.c -->
# sources/test-tools/stress-ng/test/test-munlock.c

Purpose: minimal stress-ng configure probe for the memory unlock API; it compiles and often lightly invokes `munlock`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdint.h`, `sys/mman.h`; defines `main`; calls `munlock`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdint.h`, `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-munlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-munlockall.c -->
# sources/test-tools/stress-ng/test/test-munlockall.c

Purpose: minimal stress-ng configure probe for the memory unlock-all API; it compiles and often lightly invokes `munlockall`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`; defines `main`; calls `munlockall`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-munlockall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-name-to-handle-at.c -->
# sources/test-tools/stress-ng/test/test-name-to-handle-at.c

Purpose: minimal stress-ng configure probe for the file-handle export API; it compiles and often lightly invokes `name-to-handle-at`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`; uses types `struct file_handle`; defines `main`; calls `name_to_handle_at`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-name-to-handle-at.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-nanosleep.c -->
# sources/test-tools/stress-ng/test/test-nanosleep.c

Purpose: minimal stress-ng configure probe for the relative sleep API; it compiles and often lightly invokes `nanosleep`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`; uses types `struct timespec`; defines `main`; calls `nanosleep`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-nice.c -->
# sources/test-tools/stress-ng/test/test-nice.c

Purpose: minimal stress-ng configure probe for `nice`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `nice`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-nice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off64_t.c -->
# sources/test-tools/stress-ng/test/test-off64_t.c

Purpose: compile-time availability probe for `off64_t` associated with `off64_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/types.h`; uses types `off64_t`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`; preprocessor availability gates such as `#ifndef _LARGEFILE_SOURCE`, `#ifndef _LARGEFILE64_SOURCE`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off64_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off_t.c -->
# sources/test-tools/stress-ng/test/test-off_t.c

Purpose: compile-time availability probe for `off_t` associated with `off_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/types.h`; uses types `off_t`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`; preprocessor availability gates such as `#ifndef _LARGEFILE_SOURCE`, `#ifndef _LARGEFILE64_SOURCE`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-off_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open-by-handle-at.c -->
# sources/test-tools/stress-ng/test/test-open-by-handle-at.c

Purpose: minimal stress-ng configure probe for the file-handle reopen API; it compiles and often lightly invokes `open-by-handle-at`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`; uses types `struct file_handle`; defines `main`; calls `open_by_handle_at`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open-by-handle-at.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open-tree.c -->
# sources/test-tools/stress-ng/test/test-open-tree.c

Purpose: minimal stress-ng configure probe for the Linux mount-tree open API; it compiles and often lightly invokes `open-tree`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `sys/mount.h`; defines `main`; calls `open_tree`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `fcntl.h`, `sys/mount.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_how.c -->
# sources/test-tools/stress-ng/test/test-open_how.c

Purpose: compile-time availability probe for `struct open_how` associated with `open_how`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`; uses types `struct open_how`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_how.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_memstream.c -->
# sources/test-tools/stress-ng/test/test-open_memstream.c

Purpose: minimal stress-ng configure probe for `open_memstream`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stddef.h`, `stdio.h`; defines `main`; calls `open_memstream`, `fprintf`, `fclose`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `stddef.h`, `stdio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-open_memstream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat.c -->
# sources/test-tools/stress-ng/test/test-openat.c

Purpose: minimal stress-ng configure probe for `openat`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`; defines `main`; calls `openat`; references constants/macros `AT_FDCWD`, `O_RDWR`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat2.c -->
# sources/test-tools/stress-ng/test/test-openat2.c

Purpose: minimal stress-ng configure probe for the Linux openat2 path-resolution syscall; it compiles and often lightly invokes `openat2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `linux/openat2.h`; uses types `struct open_how`; defines `main`; calls `syscall`; references constants/macros `O_RDWR`, `O_CREAT`, `RESOLVE_NO_SYMLINKS`, `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_openat2` through `syscall()`.

State and persistence behavior: may create or open a filesystem path using Linux path-resolution flags; any created file is observable host filesystem state if not removed.

Dependencies and integration points: depends on headers `unistd.h`, `sys/syscall.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `linux/openat2.h`; architecture syscall numbers `__NR_openat2`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. Test signals are successful compilation; successful linking; the expected syscall symbol being present; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-openat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-page_region.c -->
# sources/test-tools/stress-ng/test/test-page_region.c

Purpose: compile-time availability probe for `struct page_region` associated with `page_region`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/fs.h`; uses types `struct page_region`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/fs.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-page_region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pathconf.c -->
# sources/test-tools/stress-ng/test/test-pathconf.c

Purpose: minimal stress-ng configure probe for `pathconf`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `pathconf`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pathconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pause.c -->
# sources/test-tools/stress-ng/test/test-pause.c

Purpose: minimal stress-ng configure probe for the signal wait API; it compiles and often lightly invokes `pause`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `alarm`, `pause`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pause.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-personality.c -->
# sources/test-tools/stress-ng/test/test-personality.c

Purpose: minimal stress-ng configure probe for `personality`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/personality.h`; defines `main`; calls `personality`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/personality.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pid_type.c -->
# sources/test-tools/stress-ng/test/test-pid_type.c

Purpose: compile-time availability probe for `enum __pid_type` associated with `pid_type`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `fcntl.h`; uses types `enum __pid_type`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pid_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-getfd.c -->
# sources/test-tools/stress-ng/test/test-pidfd-getfd.c

Purpose: minimal stress-ng configure probe for the Linux pidfd fd-duplication API; it compiles and often lightly invokes `pidfd-getfd`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/pidfd.h`; defines `main`; calls `__has_include`, `pidfd_getfd`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/pidfd.h`; preprocessor availability gates such as `#if defined(__has_include) && __has_include(<sys/pidfd.h>)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-getfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-open.c -->
# sources/test-tools/stress-ng/test/test-pidfd-open.c

Purpose: minimal stress-ng configure probe for the Linux pidfd open API; it compiles and often lightly invokes `pidfd-open`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `sys/pidfd.h`; defines `main`; calls `pidfd_open`, `getpid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`, `sys/pidfd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-send-signal.c -->
# sources/test-tools/stress-ng/test/test-pidfd-send-signal.c

Purpose: minimal stress-ng configure probe for `pidfd-send-signal`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/syscall.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_pidfd_send_signal` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/syscall.h`; architecture syscall numbers `__NR_pidfd_send_signal`; preprocessor availability gates such as `#if !defined(__NR_pidfd_send_signal)`, `#error __NR_pidfd_send_signal not defined`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking; the expected syscall symbol being present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pidfd-send-signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pipe2.c -->
# sources/test-tools/stress-ng/test/test-pipe2.c

Purpose: minimal stress-ng configure probe for the pipe creation API; it compiles and often lightly invokes `pipe2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `unistd.h`; defines `main`; calls `pipe2`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pipe2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-alloc.c -->
# sources/test-tools/stress-ng/test/test-pkey-alloc.c

Purpose: minimal stress-ng configure probe for the memory-protection-key allocation API; it compiles and often lightly invokes `pkey-alloc`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_alloc`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-free.c -->
# sources/test-tools/stress-ng/test/test-pkey-free.c

Purpose: minimal stress-ng configure probe for the memory-protection-key release API; it compiles and often lightly invokes `pkey-free`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_free`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-free.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-get.c -->
# sources/test-tools/stress-ng/test/test-pkey-get.c

Purpose: minimal stress-ng configure probe for the memory-protection-key query API; it compiles and often lightly invokes `pkey-get`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_get`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-get.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-mprotect.c -->
# sources/test-tools/stress-ng/test/test-pkey-mprotect.c

Purpose: minimal stress-ng configure probe for the memory-protection-key mprotect API; it compiles and often lightly invokes `pkey-mprotect`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_mprotect`; references constants/macros `PROT_NONE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: changes page protections for process-local memory and does not persist outside the process.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-mprotect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-set.c -->
# sources/test-tools/stress-ng/test/test-pkey-set.c

Purpose: minimal stress-ng configure probe for the memory-protection-key rights update API; it compiles and often lightly invokes `pkey-set`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `unistd.h`, `features.h`; defines `main`; calls `pkey_set`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`, `unistd.h`, `features.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: memory-management probes are sensitive to kernel version, page alignment, architecture support, and libc header availability. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pkey-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pm_scan_arg.c -->
# sources/test-tools/stress-ng/test/test-pm_scan_arg.c

Purpose: compile-time availability probe for `struct pm_scan_arg` associated with `pm_scan_arg`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/fs.h`; uses types `struct pm_scan_arg`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/fs.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pm_scan_arg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-poll.c -->
# sources/test-tools/stress-ng/test/test-poll.c

Purpose: minimal stress-ng configure probe for the poll event API; it compiles and often lightly invokes `poll`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `poll.h`; uses types `struct pollfd`; defines `main`; calls `MAX_FDS`, `poll`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `signal.h`, `poll.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fadvise.c -->
# sources/test-tools/stress-ng/test/test-posix-fadvise.c

Purpose: minimal stress-ng configure probe for the POSIX file advice API; it compiles and often lightly invokes `posix-fadvise`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `posix_fadvise`, `endif`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error posix_fadvise is defined but not implemented and will always fail`, `#if defined(POSIX_FADV_NORMAL)`, `#if defined(POSIX_FADV_SEQUENTIAL)`, `#if defined(POSIX_FADV_RANDOM)`, `#if defined(POSIX_FADV_NOREUSE)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fadvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fallocate.c -->
# sources/test-tools/stress-ng/test/test-posix-fallocate.c

Purpose: minimal stress-ng configure probe for the file allocation API; it compiles and often lightly invokes `posix-fallocate`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `posix_fallocate`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-madvise.c -->
# sources/test-tools/stress-ng/test/test-posix-madvise.c

Purpose: minimal stress-ng configure probe for the POSIX memory advice API; it compiles and often lightly invokes `posix-madvise`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`; uses types `enum will`; defines `main`; calls `posix_madvise`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`; preprocessor availability gates such as `#if defined(POSIX_MADV_NORMAL)`, `#if defined(POSIX_MADV_RANDOM)`, `#if defined(POSIX_MADV_SEQUENTIAL)`, `#if defined(POSIX_MADV_WILLNEED)`, `#if defined(POSIX_MADV_DONTNEED)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-memalign.c -->
# sources/test-tools/stress-ng/test/test-posix-memalign.c

Purpose: minimal stress-ng configure probe for the aligned allocation API; it compiles and often lightly invokes `posix-memalign`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `posix_memalign`, `free`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-memalign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-openpt.c -->
# sources/test-tools/stress-ng/test/test-posix-openpt.c

Purpose: minimal stress-ng configure probe for the pseudo-terminal master open API; it compiles and often lightly invokes `posix-openpt`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `fcntl.h`; defines `main`; calls `posix_openpt`; references constants/macros `O_RDWR`, `O_NOCTTY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `stdlib.h`, `fcntl.h`; preprocessor availability gates such as `#if !defined(_XOPEN_SOURCE)`, `#if defined(O_RDWR)`, `#if defined(O_RDWR)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-openpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-spawn.c -->
# sources/test-tools/stress-ng/test/test-posix-spawn.c

Purpose: minimal stress-ng configure probe for the POSIX process spawn API; it compiles and often lightly invokes `posix-spawn`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stddef.h`, `spawn.h`; uses types `pid_t`; defines `main`; calls `posix_spawn`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stddef.h`, `spawn.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-posix-spawn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ppc-get-timebase.c -->
# sources/test-tools/stress-ng/test/test-ppc-get-timebase.c

Purpose: minimal stress-ng configure probe for `ppc-get-timebase`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/platform/ppc.h`; defines `main`; calls `__ppc_get_timebase`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/platform/ppc.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ppc-get-timebase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ppoll.c -->
# sources/test-tools/stress-ng/test/test-ppoll.c

Purpose: minimal stress-ng configure probe for the poll event API; it compiles and often lightly invokes `ppoll`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `poll.h`; uses types `struct pollfd`, `struct timespec`; defines `main`; calls `MAX_FDS`, `sigemptyset`, `sigaddset`, `ppoll`; references constants/macros `SIGTERM`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `signal.h`, `poll.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ppoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-inside.c -->
# sources/test-tools/stress-ng/test/test-pragma-inside.c

Purpose: minimal stress-ng configure probe for `pragma-inside`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: defines `test_pragma`, `main`; calls `_Pragma`.

Control flow: helper definitions `test_pragma` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on the C library and kernel UAPI declarations selected by the build environment. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-inside.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-no-hard-dfp.c -->
# sources/test-tools/stress-ng/test/test-pragma-no-hard-dfp.c

Purpose: minimal stress-ng configure probe for `pragma-no-hard-dfp`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: defines `main`; calls `_Pragma`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on the C library and kernel UAPI declarations selected by the build environment. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-no-hard-dfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-prefetch.c -->
# sources/test-tools/stress-ng/test/test-pragma-prefetch.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `pragma-prefetch`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdio.h`; defines `data_sum_prefetch`, `data_sum_noprefetch`, `main`; calls `_Pragma`, `printf`.

Control flow: helper definitions `data_sum_prefetch`, `data_sum_noprefetch` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma-prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma.c -->
# sources/test-tools/stress-ng/test/test-pragma.c

Purpose: minimal stress-ng configure probe for `pragma`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: defines `test_pragma`, `main`; calls `_Pragma`.

Control flow: helper definitions `test_pragma` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on the C library and kernel UAPI declarations selected by the build environment. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pragma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prctl.c -->
# sources/test-tools/stress-ng/test/test-prctl.c

Purpose: minimal stress-ng configure probe for the Linux process-control API; it compiles and often lightly invokes `prctl`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/prctl.h`; defines `main`; calls `prctl`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/prctl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pread.c -->
# sources/test-tools/stress-ng/test/test-pread.c

Purpose: minimal stress-ng configure probe for the positional read API; it compiles and often lightly invokes `pread`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; defines `main`; calls `open`, `pread`, `close`; references constants/macros `O_RDONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-preadv.c -->
# sources/test-tools/stress-ng/test/test-preadv.c

Purpose: minimal stress-ng configure probe for the vectored read API; it compiles and often lightly invokes `preadv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`; uses types `struct iovec`; defines `main`; calls `IO_LEN`, `open`, `preadv`, `close`; references constants/macros `O_RDONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-preadv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-preadv2.c -->
# sources/test-tools/stress-ng/test/test-preadv2.c

Purpose: minimal stress-ng configure probe for the vectored read API; it compiles and often lightly invokes `preadv2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`; uses types `struct iovec`; defines `main`; calls `IO_LEN`, `open`, `preadv2`, `close`; references constants/macros `O_RDONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-preadv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-priority_which_t.c -->
# sources/test-tools/stress-ng/test/test-priority_which_t.c

Purpose: minimal stress-ng configure probe for `priority_which_t`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/resource.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/resource.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-priority_which_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prlimit.c -->
# sources/test-tools/stress-ng/test/test-prlimit.c

Purpose: minimal stress-ng configure probe for the resource-limit API; it compiles and often lightly invokes `prlimit`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `sys/types.h`, `unistd.h`; uses types `struct rlimit`, `pid_t`; defines `main`; calls `getpid`, `prlimit`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-prlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-readv.c -->
# sources/test-tools/stress-ng/test/test-process-vm-readv.c

Purpose: minimal stress-ng configure probe for the cross-process readv API; it compiles and often lightly invokes `process-vm-readv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/uio.h`; uses types `struct iovec`, `pid_t`; defines `main`; calls `process_vm_readv`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/uio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-readv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-writev.c -->
# sources/test-tools/stress-ng/test/test-process-vm-writev.c

Purpose: minimal stress-ng configure probe for the cross-process writev API; it compiles and often lightly invokes `process-vm-writev`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/uio.h`; uses types `struct iovec`, `pid_t`; defines `main`; calls `process_vm_writev`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/uio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-process-vm-writev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-procmap_query.c -->
# sources/test-tools/stress-ng/test/test-procmap_query.c

Purpose: compile-time availability probe for `struct procmap_query` associated with `procmap_query`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/fs.h`; uses types `struct procmap_query`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/fs.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-procmap_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-program_invocation_name.c -->
# sources/test-tools/stress-ng/test/test-program_invocation_name.c

Purpose: minimal stress-ng configure probe for `program_invocation_name`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `errno.h`, `string.h`; defines `main`; calls `strlen`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `errno.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-program_invocation_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pselect.c -->
# sources/test-tools/stress-ng/test/test-pselect.c

Purpose: minimal stress-ng configure probe for the select event API; it compiles and often lightly invokes `pselect`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `sys/select.h`, `sys/time.h`, `sys/types.h`, `unistd.h`; uses types `struct timespec`; defines `main`; calls `MAX_FDS`, `sigemptyset`, `sigaddset`, `pselect`; references constants/macros `SIGTERM`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `signal.h`, `sys/select.h`, `sys/time.h`, `sys/types.h`, `unistd.h`; preprocessor availability gates such as `#if defined(__serenity__)`, `#error Serenity OS does not currently support pselect`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pselect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-attr-setstack.c -->
# sources/test-tools/stress-ng/test/test-pthread-attr-setstack.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-attr-setstack`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; defines `main`; calls `pthread_attr_init`, `pthread_attr_setstack`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-attr-setstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-barrier.c -->
# sources/test-tools/stress-ng/test/test-pthread-barrier.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-barrier`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; defines `main`; calls `pthread_barrier_init`, `pthread_barrier_wait`, `pthread_barrier_destroy`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-barrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutex-destroy`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutex_t`; defines `main`; calls `pthread_mutex_destroy`; references constants/macros `PTHREAD_MUTEX_INITIALIZER`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-destroy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-init.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutex-init.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutex-init`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutex_t`, `pthread_mutexattr_t`; defines `main`; calls `memset`, `pthread_mutex_init`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex_t.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutex_t.c

Purpose: compile-time availability probe for `pthread_mutex_t` associated with `pthread-mutex_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutex_t`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutex_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-destroy.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr-destroy.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutexattr-destroy`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `memset`, `pthread_mutexattr_destroy`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-destroy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-init.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr-init.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutexattr-init`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `pthread_mutexattr_init`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprioceiling.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprioceiling.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutexattr-setprioceiling`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `pthread_mutexattr_init`, `pthread_mutexattr_setprioceiling`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprioceiling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprotocol.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprotocol.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutexattr-setprotocol`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `pthread_mutexattr_init`, `pthread_mutexattr_setprotocol`; references constants/macros `PTHREAD_PRIO_INHERIT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setprotocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setrobust.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr-setrobust.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-mutexattr-setrobust`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `pthread_mutexattr_setrobust`; references constants/macros `PTHREAD_MUTEX_ROBUST`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr-setrobust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr_t.c -->
# sources/test-tools/stress-ng/test/test-pthread-mutexattr_t.c

Purpose: compile-time availability probe for `pthread_mutexattr_t` associated with `pthread-mutexattr_t`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `pthread_mutexattr_t`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-mutexattr_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-inherit.c -->
# sources/test-tools/stress-ng/test/test-pthread-prio-inherit.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-prio-inherit`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; defines `main`; references constants/macros `PTHREAD_PRIO_INHERIT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-inherit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-none.c -->
# sources/test-tools/stress-ng/test/test-pthread-prio-none.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-prio-none`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; defines `main`; references constants/macros `PTHREAD_PRIO_NONE`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-protect.c -->
# sources/test-tools/stress-ng/test/test-pthread-prio-protect.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-prio-protect`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`; defines `main`; references constants/macros `PTHREAD_PRIO_PROTECT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-prio-protect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-setaffinity-np.c -->
# sources/test-tools/stress-ng/test/test-pthread-setaffinity-np.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-setaffinity-np`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; defines `main`; calls `memset`, `pthread_setaffinity_np`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-setaffinity-np.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-setschedparam.c -->
# sources/test-tools/stress-ng/test/test-pthread-setschedparam.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread-setschedparam`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `pthread.h`, `string.h`; uses types `struct sched_param`; defines `main`; calls `memset`, `pthread_setschedparam`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `pthread.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread-setschedparam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread_sigqueue.c -->
# sources/test-tools/stress-ng/test/test-pthread_sigqueue.c

Purpose: minimal stress-ng configure probe for the pthread API; it compiles and often lightly invokes `pthread_sigqueue`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `string.h`, `pthread.h`; uses types `union sigval`; defines `main`; calls `memset`, `pthread_sigqueue`; references constants/macros `SIGKILL`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses in-process pthread objects, attributes, or scheduling state that ends with process exit.

Dependencies and integration points: depends on headers `signal.h`, `string.h`, `pthread.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size; pthread link compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pthread_sigqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptrace.c -->
# sources/test-tools/stress-ng/test/test-ptrace.c

Purpose: minimal stress-ng configure probe for the ptrace tracing API; it compiles and often lightly invokes `ptrace`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/ptrace.h`; defines `main`; calls `NULL`, `ptrace`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/ptrace.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptrace_request.c -->
# sources/test-tools/stress-ng/test/test-ptrace_request.c

Purpose: compile-time availability probe for `enum __ptrace_request` associated with `ptrace_request`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/ptrace.h`; uses types `enum __ptrace_request`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/ptrace.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptrace_request.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptsname.c -->
# sources/test-tools/stress-ng/test/test-ptsname.c

Purpose: minimal stress-ng configure probe for the pseudoterminal slave-name API; it compiles and often lightly invokes `ptsname`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `ptsname`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ptsname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwrite.c -->
# sources/test-tools/stress-ng/test/test-pwrite.c

Purpose: minimal stress-ng configure probe for the positional write API; it compiles and often lightly invokes `pwrite`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; defines `main`; calls `open`, `pwrite`, `close`; references constants/macros `O_WRONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwritev.c -->
# sources/test-tools/stress-ng/test/test-pwritev.c

Purpose: minimal stress-ng configure probe for the vectored write API; it compiles and often lightly invokes `pwritev`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`; uses types `struct iovec`; defines `main`; calls `open`, `pwritev`, `close`; references constants/macros `O_WRONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwritev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwritev2.c -->
# sources/test-tools/stress-ng/test/test-pwritev2.c

Purpose: minimal stress-ng configure probe for the vectored write API; it compiles and often lightly invokes `pwritev2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`; uses types `struct iovec`; defines `main`; calls `open`, `pwritev2`, `close`; references constants/macros `O_WRONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-pwritev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-qsort.c -->
# sources/test-tools/stress-ng/test/test-qsort.c

Purpose: minimal stress-ng configure probe for the libc qsort API; it compiles and often lightly invokes `qsort`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`; defines `cmp`, `main`; calls `qsort`.

Control flow: helper definitions `cmp` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `stdio.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-qsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-quotactl-fd.c -->
# sources/test-tools/stress-ng/test/test-quotactl-fd.c

Purpose: minimal stress-ng configure probe for the quota control fd API; it compiles and often lightly invokes `quotactl-fd`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/quota.h`; defines `main`; calls `quotactl_fd`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/quota.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: privilege-sensitive APIs can fail under ordinary users, containers, or restricted capabilities. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-quotactl-fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-radixsort.c -->
# sources/test-tools/stress-ng/test/test-radixsort.c

Purpose: minimal stress-ng configure probe for the BSD radixsort API; it compiles and often lightly invokes `radixsort`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `radixsort`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-radixsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-random.c -->
# sources/test-tools/stress-ng/test/test-random.c

Purpose: minimal stress-ng configure probe for the libc PRNG API; it compiles and often lightly invokes `random`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `random`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readahead.c -->
# sources/test-tools/stress-ng/test/test-readahead.c

Purpose: minimal stress-ng configure probe for the file readahead API; it compiles and often lightly invokes `readahead`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`; defines `main`; calls `readahead`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readlinkat.c -->
# sources/test-tools/stress-ng/test/test-readlinkat.c

Purpose: minimal stress-ng configure probe for the readlinkat API; it compiles and often lightly invokes `readlinkat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `readlinkat`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readv.c -->
# sources/test-tools/stress-ng/test/test-readv.c

Purpose: minimal stress-ng configure probe for the vectored read API; it compiles and often lightly invokes `readv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`; uses types `struct iovec`; defines `main`; calls `IO_LEN`, `open`, `readv`, `close`; references constants/macros `O_RDONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/uio.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-readv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-recvmmsg.c -->
# sources/test-tools/stress-ng/test/test-recvmmsg.c

Purpose: minimal stress-ng configure probe for the batched socket receive API; it compiles and often lightly invokes `recvmmsg`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`; uses types `struct sockaddr_in`, `struct mmsghdr`, `struct iovec`, `struct timespec`, `struct sockaddr`; defines `main`; calls `memset`, `socket`, `htonl`, `htons`, `bind`, `close`, `recvmmsg`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-recvmmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-recvmsg.c -->
# sources/test-tools/stress-ng/test/test-recvmsg.c

Purpose: minimal stress-ng configure probe for the socket message receive API; it compiles and often lightly invokes `recvmsg`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`; uses types `struct sockaddr_in`, `struct msghdr`, `struct iovec`, `struct timespec`, `struct sockaddr`; defines `main`; calls `memset`, `socket`, `htonl`, `htons`, `bind`, `close`, `recvmsg`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-recvmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regcomp.c -->
# sources/test-tools/stress-ng/test/test-regcomp.c

Purpose: minimal stress-ng configure probe for the POSIX regex compile API; it compiles and often lightly invokes `regcomp`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `regex.h`; defines `main`; calls `regcomp`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `regex.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regcomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regerror.c -->
# sources/test-tools/stress-ng/test/test-regerror.c

Purpose: minimal stress-ng configure probe for the POSIX regex compile API; it compiles and often lightly invokes `regerror`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stddef.h`, `regex.h`; defines `main`; calls `regcomp`, `regerror`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stddef.h`, `regex.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regexec.c -->
# sources/test-tools/stress-ng/test/test-regexec.c

Purpose: minimal stress-ng configure probe for the POSIX regex compile API; it compiles and often lightly invokes `regexec`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `regex.h`; defines `main`; calls `regcomp`, `regexec`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `regex.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regfree.c -->
# sources/test-tools/stress-ng/test/test-regfree.c

Purpose: minimal stress-ng configure probe for the POSIX regex compile API; it compiles and often lightly invokes `regfree`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `regex.h`; defines `main`; calls `regcomp`, `regfree`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `regex.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-regfree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-remap-file-pages.c -->
# sources/test-tools/stress-ng/test/test-remap-file-pages.c

Purpose: minimal stress-ng configure probe for `remap-file-pages`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/mman.h`; defines `main`; calls `remap_file_pages`; references constants/macros `MAP_SHARED`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-remap-file-pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-removexattr.c -->
# sources/test-tools/stress-ng/test/test-removexattr.c

Purpose: minimal stress-ng configure probe for the extended-attribute remove API; it compiles and often lightly invokes `removexattr`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`; defines `main`; calls `removexattr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-removexattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-removexattrat.c -->
# sources/test-tools/stress-ng/test/test-removexattrat.c

Purpose: minimal stress-ng configure probe for the extended-attribute remove API; it compiles and often lightly invokes `removexattrat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`; defines `main`; calls `removexattrat`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-removexattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-renameat.c -->
# sources/test-tools/stress-ng/test/test-renameat.c

Purpose: minimal stress-ng configure probe for the renameat API; it compiles and often lightly invokes `renameat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdio.h`, `fcntl.h`; defines `main`; calls `renameat`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdio.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-renameat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-renameat2.c -->
# sources/test-tools/stress-ng/test/test-renameat2.c

Purpose: minimal stress-ng configure probe for the renameat2 API; it compiles and often lightly invokes `renameat2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdio.h`, `fcntl.h`; defines `main`; calls `renameat2`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdio.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-renameat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rfork.c -->
# sources/test-tools/stress-ng/test/test-rfork.c

Purpose: minimal stress-ng configure probe for `rfork`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`; uses types `pid_t`; defines `main`; calls `rfork`, `exit`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rfork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rlimit_resource_t.c -->
# sources/test-tools/stress-ng/test/test-rlimit_resource_t.c

Purpose: minimal stress-ng configure probe for `rlimit_resource_t`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/resource.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/resource.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rlimit_resource_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rseq_slice_yield.c -->
# sources/test-tools/stress-ng/test/test-rseq_slice_yield.c

Purpose: minimal stress-ng configure probe for `rseq_slice_yield`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `rseq_slice_yield`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rseq_slice_yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rtc_param.c -->
# sources/test-tools/stress-ng/test/test-rtc_param.c

Purpose: compile-time availability probe for `struct rtc_param` associated with `rtc_param`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/rtc.h`; uses types `struct rtc_param`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/rtc.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rtc_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_maxrss.c -->
# sources/test-tools/stress-ng/test/test-rusage_ru_maxrss.c

Purpose: compile-time availability probe for `struct rusage` associated with `rusage_ru_maxrss`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `string.h`; uses types `struct rusage`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_maxrss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c -->
# sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c

Purpose: compile-time availability probe for `struct rusage` associated with `rusage_ru_minflt`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `string.h`; uses types `struct rusage`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_minflt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_nvcsw.c -->
# sources/test-tools/stress-ng/test/test-rusage_ru_nvcsw.c

Purpose: compile-time availability probe for `struct rusage` associated with `rusage_ru_nvcsw`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`, `string.h`; uses types `struct rusage`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_ru_nvcsw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_who_t.c -->
# sources/test-tools/stress-ng/test/test-rusage_who_t.c

Purpose: minimal stress-ng configure probe for `rusage_who_t`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/resource.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/resource.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-rusage_who_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sbrk.c -->
# sources/test-tools/stress-ng/test/test-sbrk.c

Purpose: minimal stress-ng configure probe for `sbrk`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `sbrk`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sbrk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-get-priority-max.c -->
# sources/test-tools/stress-ng/test/test-sched-get-priority-max.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-get-priority-max`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `sched_get_priority_max`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-get-priority-max.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-get-priority-min.c -->
# sources/test-tools/stress-ng/test/test-sched-get-priority-min.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-get-priority-min`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `sched_get_priority_min`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-get-priority-min.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-getaffinity.c -->
# sources/test-tools/stress-ng/test/test-sched-getaffinity.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-getaffinity`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `sched_getaffinity`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-getaffinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-getcpu.c -->
# sources/test-tools/stress-ng/test/test-sched-getcpu.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-getcpu`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `sched_getcpu`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-rr-get-interval.c -->
# sources/test-tools/stress-ng/test/test-sched-rr-get-interval.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-rr-get-interval`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; uses types `struct timespec`, `pid_t`; defines `main`; calls `sched_rr_get_interval`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-rr-get-interval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-setaffinity.c -->
# sources/test-tools/stress-ng/test/test-sched-setaffinity.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-setaffinity`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `string.h`, `sched.h`; defines `main`; calls `memset`, `sched_setaffinity`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `string.h`, `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-setaffinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-setscheduler.c -->
# sources/test-tools/stress-ng/test/test-sched-setscheduler.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-setscheduler`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; uses types `struct sched_param`; defines `main`; calls `sched_setscheduler`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-setscheduler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-yield.c -->
# sources/test-tools/stress-ng/test/test-sched-yield.c

Purpose: minimal stress-ng configure probe for the scheduler API; it compiles and often lightly invokes `sched-yield`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `sched_yield`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sched-yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assoc_stats.c -->
# sources/test-tools/stress-ng/test/test-sctp_assoc_stats.c

Purpose: compile-time availability probe for `struct sctp_assoc_stats` associated with `sctp_assoc_stats`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_assoc_stats`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assoc_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assoc_value.c -->
# sources/test-tools/stress-ng/test/test-sctp_assoc_value.c

Purpose: compile-time availability probe for `struct sctp_assoc_value` associated with `sctp_assoc_value`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_assoc_value`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assoc_value.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assocparams.c -->
# sources/test-tools/stress-ng/test/test-sctp_assocparams.c

Purpose: compile-time availability probe for `struct sctp_assocparams` associated with `sctp_assocparams`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_assocparams`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_assocparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_default_prinfo.c -->
# sources/test-tools/stress-ng/test/test-sctp_default_prinfo.c

Purpose: compile-time availability probe for `struct sctp_default_prinfo` associated with `sctp_default_prinfo`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_default_prinfo`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_default_prinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_event_subscribe.c -->
# sources/test-tools/stress-ng/test/test-sctp_event_subscribe.c

Purpose: compile-time availability probe for `struct sctp_event_subscribe` associated with `sctp_event_subscribe`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_event_subscribe`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_event_subscribe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_getaddrs.c -->
# sources/test-tools/stress-ng/test/test-sctp_getaddrs.c

Purpose: compile-time availability probe for `struct sctp_getaddrs` associated with `sctp_getaddrs`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_getaddrs`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_getaddrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_initmsg.c -->
# sources/test-tools/stress-ng/test/test-sctp_initmsg.c

Purpose: compile-time availability probe for `struct sctp_initmsg` associated with `sctp_initmsg`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_initmsg`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_initmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrinfo.c -->
# sources/test-tools/stress-ng/test/test-sctp_paddrinfo.c

Purpose: compile-time availability probe for `struct sctp_paddrinfo` associated with `sctp_paddrinfo`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_paddrinfo`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrparams.c -->
# sources/test-tools/stress-ng/test/test-sctp_paddrparams.c

Purpose: compile-time availability probe for `struct sctp_paddrparams` associated with `sctp_paddrparams`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_paddrparams`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_prim.c -->
# sources/test-tools/stress-ng/test/test-sctp_prim.c

Purpose: compile-time availability probe for `struct sctp_prim` associated with `sctp_prim`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_prim`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_prim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_probeinterval.c -->
# sources/test-tools/stress-ng/test/test-sctp_probeinterval.c

Purpose: compile-time availability probe for `struct sctp_probeinterval` associated with `sctp_probeinterval`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_probeinterval`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_probeinterval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_rtoinfo.c -->
# sources/test-tools/stress-ng/test/test-sctp_rtoinfo.c

Purpose: compile-time availability probe for `struct sctp_rtoinfo` associated with `sctp_rtoinfo`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_rtoinfo`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_rtoinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_sched_type.c -->
# sources/test-tools/stress-ng/test/test-sctp_sched_type.c

Purpose: compile-time availability probe for `enum sctp_sched_type` associated with `sctp_sched_type`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `enum sctp_sched_type`; defines `main`; references constants/macros `SCTP_SS_FCFS`, `SCTP_SS_PRIO`, `SCTP_SS_RR`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: scheduler and pthread probes can be affected by libc feature macros, realtime privileges, and platform-specific optional constants. SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_sched_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_setadaption.c -->
# sources/test-tools/stress-ng/test/test-sctp_setadaption.c

Purpose: compile-time availability probe for `struct sctp_setadaptation` associated with `sctp_setadaption`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_setadaptation`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_setadaption.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_status.c -->
# sources/test-tools/stress-ng/test/test-sctp_status.c

Purpose: compile-time availability probe for `struct sctp_status` associated with `sctp_status`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_status`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_stream_value.c -->
# sources/test-tools/stress-ng/test/test-sctp_stream_value.c

Purpose: compile-time availability probe for `struct sctp_stream_value` associated with `sctp_stream_value`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_stream_value`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_stream_value.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_udpencaps.c -->
# sources/test-tools/stress-ng/test/test-sctp_udpencaps.c

Purpose: compile-time availability probe for `struct sctp_udpencaps` associated with `sctp_udpencaps`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_udpencaps`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_udpencaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c -->
# sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c

Purpose: compile-time availability probe for `struct seccomp_notif_sizes` associated with `seccomp_notif_sizes`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `stdlib.h`, `linux/seccomp.h`; uses types `struct seccomp_notif_sizes`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `linux/seccomp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seccomp_notif_sizes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seed48.c -->
# sources/test-tools/stress-ng/test/test-seed48.c

Purpose: minimal stress-ng configure probe for the libc 48-bit PRNG seed exchange API; it compiles and often lightly invokes `seed48`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `seed48`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-seed48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-select.c -->
# sources/test-tools/stress-ng/test/test-select.c

Purpose: minimal stress-ng configure probe for the select event API; it compiles and often lightly invokes `select`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`, `sys/select.h`; uses types `struct timeval`; defines `main`; calls `select`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`, `sys/select.h`; preprocessor availability gates such as `#if defined(__serenity__)`, `#error Serenity OS does not currently support pselect`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-select.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-posix.c -->
# sources/test-tools/stress-ng/test/test-sem-posix.c

Purpose: minimal stress-ng configure probe for `sem-posix`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `time.h`, `semaphore.h`; uses types `struct timespec`; defines `main`; calls `sem_init`, `sem_wait`, `sem_post`, `sem_trywait`, `sem_timedwait`, `sem_destroy`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`, `semaphore.h`; preprocessor availability gates such as `#if defined(__FreeBSD_kernel__)`, `#error POSIX semaphores not yet implemented`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-sysv.c -->
# sources/test-tools/stress-ng/test/test-sem-sysv.c

Purpose: minimal stress-ng configure probe for the System V semaphore API; it compiles and often lightly invokes `sem-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`, `sys/types.h`, `sys/ipc.h`, `sys/sem.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; uses types `struct semid_ds`, `struct seminfo`, `struct sembuf`, `struct timespec`, `union _semun`; defines `main`; calls `getpid`, `semget`, `semctl`, `clock_gettime`, `semtimedop`, `semop`; references constants/macros `IPC_STAT`, `IPC_SET`, `IPC_INFO`, `IPC_CREAT`, `IPC_RMID`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V semaphore set and removes it through `IPC_RMID`; semaphore values are transient kernel IPC state.

Dependencies and integration points: depends on headers `time.h`, `sys/types.h`, `sys/ipc.h`, `sys/sem.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error semop, semget and semctl are not implemented`, `#if defined(__linux__)`, `#if defined(IPC_STAT)`, `#if defined(SEM_STAT)`, `#if defined(IPC_INFO) &&	\`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sem-sysv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-semtimedop.c -->
# sources/test-tools/stress-ng/test/test-semtimedop.c

Purpose: minimal stress-ng configure probe for `semtimedop`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `sys/ipc.h`, `sys/sem.h`; uses types `struct sembuf`, `struct timespec`; defines `main`; calls `semtimedop`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/ipc.h`, `sys/sem.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-semtimedop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendfile.c -->
# sources/test-tools/stress-ng/test/test-sendfile.c

Purpose: minimal stress-ng configure probe for the zero-copy file transfer API; it compiles and often lightly invokes `sendfile`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/sendfile.h`; uses types `off_t`; defines `main`; calls `sendfile`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/sendfile.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmmsg.c -->
# sources/test-tools/stress-ng/test/test-sendmmsg.c

Purpose: minimal stress-ng configure probe for the batched socket send API; it compiles and often lightly invokes `sendmmsg`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`; uses types `struct sockaddr_in`, `struct mmsghdr`, `struct iovec`, `struct sockaddr`; defines `main`; calls `memset`, `socket`, `htonl`, `htons`, `connect`, `close`, `sendmmsg`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmsg.c -->
# sources/test-tools/stress-ng/test/test-sendmsg.c

Purpose: minimal stress-ng configure probe for the socket message send API; it compiles and often lightly invokes `sendmsg`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`; uses types `struct sockaddr_in`, `struct msghdr`, `struct iovec`, `struct sockaddr`; defines `main`; calls `memset`, `socket`, `htonl`, `htons`, `connect`, `close`, `sendmsg`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `unistd.h`, `netinet/ip.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/types.h`, `sys/socket.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sendmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-serial-icounter.c -->
# sources/test-tools/stress-ng/test/test-serial-icounter.c

Purpose: compile-time availability probe for `struct serial_icounter_struct` associated with `serial-icounter`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/serial.h`; uses types `struct serial_icounter_struct`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/serial.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-serial-icounter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-serial-struct.c -->
# sources/test-tools/stress-ng/test/test-serial-struct.c

Purpose: compile-time availability probe for `struct serial_struct` associated with `serial-struct`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/serial.h`, `string.h`; uses types `struct serial_struct`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/serial.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-serial-struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setdomainname.c -->
# sources/test-tools/stress-ng/test/test-setdomainname.c

Purpose: minimal stress-ng configure probe for `setdomainname`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `string.h`; defines `main`; calls `getdomainname`, `setdomainname`, `strlen`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setdomainname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setfsgid.c -->
# sources/test-tools/stress-ng/test/test-setfsgid.c

Purpose: minimal stress-ng configure probe for `setfsgid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/fsuid.h`; defines `main`; calls `setfsgid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/fsuid.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setfsgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setfsuid.c -->
# sources/test-tools/stress-ng/test/test-setfsuid.c

Purpose: minimal stress-ng configure probe for `setfsuid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/fsuid.h`; defines `main`; calls `setfsuid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/fsuid.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setfsuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setgroups.c -->
# sources/test-tools/stress-ng/test/test-setgroups.c

Purpose: minimal stress-ng configure probe for `setgroups`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `grp.h`; defines `main`; calls `setgroups`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`, `grp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setitimer.c -->
# sources/test-tools/stress-ng/test/test-setitimer.c

Purpose: minimal stress-ng configure probe for the interval timer API; it compiles and often lightly invokes `setitimer`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `string.h`, `sys/time.h`; uses types `struct itimerval`; defines `main`; calls `memset`, `setitimer`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `string.h`, `sys/time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setitimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setmntent.c -->
# sources/test-tools/stress-ng/test/test-setmntent.c

Purpose: minimal stress-ng configure probe for `setmntent`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stdio.h`, `mntent.h`; defines `main`; calls `setmntent`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `stdio.h`, `mntent.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setmntent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setns.c -->
# sources/test-tools/stress-ng/test/test-setns.c

Purpose: minimal stress-ng configure probe for the namespace switching API; it compiles and often lightly invokes `setns`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `sched.h`; defines `main`; calls `open`, `setns`, `close`; references constants/macros `O_RDONLY`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpgid.c -->
# sources/test-tools/stress-ng/test/test-setpgid.c

Purpose: minimal stress-ng configure probe for `setpgid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setpgid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpgrp.c -->
# sources/test-tools/stress-ng/test/test-setpgrp.c

Purpose: minimal stress-ng configure probe for `setpgrp`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setpgrp`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpriority.c -->
# sources/test-tools/stress-ng/test/test-setpriority.c

Purpose: minimal stress-ng configure probe for `setpriority`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/time.h`, `sys/resource.h`; defines `main`; calls `setpriority`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/time.h`, `sys/resource.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpriority.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle.c -->
# sources/test-tools/stress-ng/test/test-setproctitle.c

Purpose: minimal stress-ng configure probe for `setproctitle`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `bsd/unistd.h`; defines `main`; calls `setproctitle_init`, `setproctitle`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`, `bsd/unistd.h`; preprocessor availability gates such as `#if !(defined(__APPLE__) || \`, `#if !(defined(__APPLE__) || \`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle_init.c -->
# sources/test-tools/stress-ng/test/test-setproctitle_init.c

Purpose: minimal stress-ng configure probe for `setproctitle_init`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `bsd/unistd.h`; defines `main`; calls `setproctitle_init`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `unistd.h`, `bsd/unistd.h`; preprocessor availability gates such as `#if !(defined(__APPLE__) || \`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setproctitle_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpwent.c -->
# sources/test-tools/stress-ng/test/test-setpwent.c

Purpose: minimal stress-ng configure probe for `setpwent`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `pwd.h`; defines `main`; calls `setpwent`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `pwd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setregid.c -->
# sources/test-tools/stress-ng/test/test-setregid.c

Purpose: minimal stress-ng configure probe for `setregid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setregid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setregid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setresgid.c -->
# sources/test-tools/stress-ng/test/test-setresgid.c

Purpose: minimal stress-ng configure probe for `setresgid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setresgid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setresgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setresuid.c -->
# sources/test-tools/stress-ng/test/test-setresuid.c

Purpose: minimal stress-ng configure probe for `setresuid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setresuid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setresuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setreuid.c -->
# sources/test-tools/stress-ng/test/test-setreuid.c

Purpose: minimal stress-ng configure probe for `setreuid`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`; defines `main`; calls `setreuid`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setreuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-settimeofday.c -->
# sources/test-tools/stress-ng/test/test-settimeofday.c

Purpose: minimal stress-ng configure probe for the time-setting API; it compiles and often lightly invokes `settimeofday`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/time.h`, `string.h`; uses types `struct timeval`; defines `main`; calls `memset`, `settimeofday`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/time.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: privilege-sensitive APIs can fail under ordinary users, containers, or restricted capabilities. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-settimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattr.c -->
# sources/test-tools/stress-ng/test/test-setxattr.c

Purpose: minimal stress-ng configure probe for the extended-attribute set API; it compiles and often lightly invokes `setxattr`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`; defines `main`; calls `setxattr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattrat.c -->
# sources/test-tools/stress-ng/test/test-setxattrat.c

Purpose: minimal stress-ng configure probe for the extended-attribute set API; it compiles and often lightly invokes `setxattrat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`; uses types `struct xattr_args`; defines `main`; calls `setxattrat`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe may transiently alter process-local attributes such as scheduling, identity, personality, signal, or control flags. Those changes are scoped to the short-lived probe process unless the kernel API itself has broader privilege effects.

Dependencies and integration points: depends on headers `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-setxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-open.c -->
# sources/test-tools/stress-ng/test/test-shm-open.c

Purpose: minimal stress-ng configure probe for the POSIX shared-memory API; it compiles and often lightly invokes `shm-open`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mman.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`; defines `main`; calls `shm_open`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/mman.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-sysv.c -->
# sources/test-tools/stress-ng/test/test-shm-sysv.c

Purpose: minimal stress-ng configure probe for the System V shared-memory API; it compiles and often lightly invokes `shm-sysv`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/ipc.h`, `sys/shm.h`, `sys/stat.h`, `fcntl.h`; uses types `struct shmid_ds`, `struct shminfo`, `struct shm_info`; defines `main`; calls `getpid`, `shmget`, `shmat`, `shmctl`, `endif`, `shmdt`; references constants/macros `IPC_CREAT`, `IPC_EXCL`, `IPC_STAT`, `IPC_INFO`, `IPC_RMID`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: allocates a System V shared-memory segment and removes it through `IPC_RMID`; attachment state is transient.

Dependencies and integration points: depends on headers `unistd.h`, `sys/ipc.h`, `sys/shm.h`, `sys/stat.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(IPC_STAT)`, `#if defined(__linux__) &&	\`, `#if defined(__linux__) &&	\`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-sysv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-unlink.c -->
# sources/test-tools/stress-ng/test/test-shm-unlink.c

Purpose: minimal stress-ng configure probe for `shm-unlink`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/mman.h`; defines `main`; calls `shm_unlink`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mman.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shm-unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shmid-ds.c -->
# sources/test-tools/stress-ng/test/test-shmid-ds.c

Purpose: compile-time availability probe for `struct shmid_ds` associated with `shmid-ds`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/ipc.h`, `sys/shm.h`; uses types `struct shmid_ds`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/ipc.h`, `sys/shm.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shmid-ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shminfo.c -->
# sources/test-tools/stress-ng/test/test-shminfo.c

Purpose: compile-time availability probe for `struct shminfo` associated with `shminfo`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/ipc.h`, `sys/shm.h`; uses types `struct shminfo`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/ipc.h`, `sys/shm.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-shminfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigaltstack.c -->
# sources/test-tools/stress-ng/test/test-sigaltstack.c

Purpose: minimal stress-ng configure probe for `sigaltstack`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stdio.h`, `signal.h`; defines `main`; calls `sigaltstack`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdio.h`, `signal.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigaltstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-siglongjmp.c -->
# sources/test-tools/stress-ng/test/test-siglongjmp.c

Purpose: minimal stress-ng configure probe for `siglongjmp`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `setjmp.h`; defines `main`; calls `sigsetjmp`, `siglongjmp`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `setjmp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-siglongjmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-signalfd.c -->
# sources/test-tools/stress-ng/test/test-signalfd.c

Purpose: minimal stress-ng configure probe for `signalfd`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/signalfd.h`, `string.h`; defines `main`; calls `memset`, `signalfd`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/signalfd.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-signalfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigqueue.c -->
# sources/test-tools/stress-ng/test/test-sigqueue.c

Purpose: minimal stress-ng configure probe for `sigqueue`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `signal.h`; uses types `union sigval`, `pid_t`; defines `main`; calls `getpid`, `sigqueue`; references constants/macros `SIGALRM`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`, `signal.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error sigqueue is defined but not implemented and will always fail`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigwaitinfo.c -->
# sources/test-tools/stress-ng/test/test-sigwaitinfo.c

Purpose: minimal stress-ng configure probe for `sigwaitinfo`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/types.h`, `unistd.h`, `signal.h`; defines `main`; calls `sigemptyset`, `sigaddset`, `sigwaitinfo`; references constants/macros `SIGUSR1`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/types.h`, `unistd.h`, `signal.h`; preprocessor availability gates such as `#if defined(__gnu_hurd__)`, `#error sigwaitinfo is defined but not implemented and will always fail`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sigwaitinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-snd_ctl_card_info.c -->
# sources/test-tools/stress-ng/test/test-snd_ctl_card_info.c

Purpose: compile-time availability probe for `struct snd_ctl_card_info` associated with `snd_ctl_card_info`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sound/asound.h`; uses types `struct snd_ctl_card_info`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sound/asound.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: ALSA structure probes require ALSA development headers and can fail early on minimal systems. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-snd_ctl_card_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-snd_ctl_tlv.c -->
# sources/test-tools/stress-ng/test/test-snd_ctl_tlv.c

Purpose: compile-time availability probe for `struct snd_ctl_tlv` associated with `snd_ctl_tlv`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sound/asound.h`; uses types `struct snd_ctl_tlv`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sound/asound.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: ALSA structure probes require ALSA development headers and can fail early on minimal systems. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-snd_ctl_tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sock-diag.c -->
# sources/test-tools/stress-ng/test/test-sock-diag.c

Purpose: minimal stress-ng configure probe for `sock-diag`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`, `linux/netlink.h`, `linux/rtnetlink.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `errno.h`, `stdio.h`, `string.h`, `unistd.h`, `sys/socket.h`, `sys/un.h`, `linux/netlink.h`, `linux/rtnetlink.h`, `linux/sock_diag.h`, `linux/unix_diag.h`; preprocessor availability gates such as `#if defined(__linux__)`, `#if defined(AF_NETLINK) &&		\`, `#error sock_diag not supported`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sock-diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sockaddr_un.c -->
# sources/test-tools/stress-ng/test/test-sockaddr_un.c

Purpose: compile-time availability probe for `struct sockaddr_un` associated with `sockaddr_un`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/socket.h`, `sys/un.h`; uses types `struct sockaddr_un`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: uses socket descriptors and address structures; network/socket state is process-local unless a bind path or port is created.

Dependencies and integration points: depends on headers `sys/socket.h`, `sys/un.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sockaddr_un.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-splice.c -->
# sources/test-tools/stress-ng/test/test-splice.c

Purpose: minimal stress-ng configure probe for the pipe splice API; it compiles and often lightly invokes `splice`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `stdlib.h`; defines `main`; calls `splice`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`, `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-srand48.c -->
# sources/test-tools/stress-ng/test/test-srand48.c

Purpose: minimal stress-ng configure probe for the libc 48-bit PRNG seeding API; it compiles and often lightly invokes `srand48`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `srand`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-srand48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-srandom.c -->
# sources/test-tools/stress-ng/test/test-srandom.c

Purpose: minimal stress-ng configure probe for the libc PRNG API; it compiles and often lightly invokes `srandom`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdlib.h`; defines `main`; calls `srandom`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdlib.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-srandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-stat.c -->
# sources/test-tools/stress-ng/test/test-stat.c

Purpose: minimal stress-ng configure probe for the file stat API; it compiles and often lightly invokes `stat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`; uses types `struct stat`; defines `main`; calls `stat`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-statfs.c -->
# sources/test-tools/stress-ng/test/test-statfs.c

Purpose: minimal stress-ng configure probe for the filesystem stat API; it compiles and often lightly invokes `statfs`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/vfs.h`; uses types `struct statfs`; defines `main`; calls `statfs`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `sys/vfs.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-statfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-statx.c -->
# sources/test-tools/stress-ng/test/test-statx.c

Purpose: minimal stress-ng configure probe for the Linux statx API; it compiles and often lightly invokes `statx`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `sys/stat.h`; uses types `struct statx`; defines `main`; calls `statx`; references constants/macros `AT_STATX_SYNC_AS_STAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: the probe works through ordinary file descriptors or metadata buffers. Any filesystem side effects are limited to the explicit path operations visible in the source.

Dependencies and integration points: depends on headers `fcntl.h`, `sys/stat.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-stime.c -->
# sources/test-tools/stress-ng/test/test-stime.c

Purpose: minimal stress-ng configure probe for `stime`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `time.h`, `string.h`; defines `main`; calls `memset`, `stime`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-stime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-strfunc.c -->
# sources/test-tools/stress-ng/test/test-strfunc.c

Purpose: minimal stress-ng configure probe for `strfunc`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `stddef.h`, `stdlib.h`, `string.h`, `bsd/string.h`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stddef.h`, `stdlib.h`, `string.h`, `bsd/string.h`; preprocessor availability gates such as `#if !(defined(__APPLE__) || \`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-strfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-swap.c -->
# sources/test-tools/stress-ng/test/test-swap.c

Purpose: minimal stress-ng configure probe for `swap`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `unistd.h`, `sys/swap.h`; defines `main`; calls `swapon`, `swapoff`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `sys/swap.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-swapcontext.c -->
# sources/test-tools/stress-ng/test/test-swapcontext.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `swapcontext`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `ucontext.h`; defines `func`, `main`; calls `getcontext`, `makecontext`, `swapcontext`.

Control flow: helper definitions `func` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `ucontext.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-swapcontext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-symlinkat.c -->
# sources/test-tools/stress-ng/test/test-symlinkat.c

Purpose: minimal stress-ng configure probe for the symlinkat API; it compiles and often lightly invokes `symlinkat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`, `unistd.h`; defines `main`; calls `symlinkat`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-symlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-bool-compare-and-swap.c -->
# sources/test-tools/stress-ng/test/test-sync-bool-compare-and-swap.c

Purpose: minimal stress-ng configure probe for the system sync API; it compiles and often lightly invokes `sync-bool-compare-and-swap`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdint.h`; defines `main`; calls `__sync_bool_compare_and_swap`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdint.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-bool-compare-and-swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-file-range.c -->
# sources/test-tools/stress-ng/test/test-sync-file-range.c

Purpose: minimal stress-ng configure probe for the file-range sync API; it compiles and often lightly invokes `sync-file-range`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`; defines `main`; calls `sync_file_range`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-file-range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-synchronize.c -->
# sources/test-tools/stress-ng/test/test-sync-synchronize.c

Purpose: minimal stress-ng configure probe for the system sync API; it compiles and often lightly invokes `sync-synchronize`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: defines `main`; calls `__sync_synchronize`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on the C library and kernel UAPI declarations selected by the build environment. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync-synchronize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync.c -->
# sources/test-tools/stress-ng/test/test-sync.c

Purpose: minimal stress-ng configure probe for the system sync API; it compiles and often lightly invokes `sync`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `sync`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync_val_compare_and_swap.c -->
# sources/test-tools/stress-ng/test/test-sync_val_compare_and_swap.c

Purpose: minimal stress-ng configure probe for the system sync API; it compiles and often lightly invokes `sync_val_compare_and_swap`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `stdint.h`; defines `main`; calls `__sync_val_compare_and_swap`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `stdint.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sync_val_compare_and_swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syncfs.c -->
# sources/test-tools/stress-ng/test/test-syncfs.c

Purpose: minimal stress-ng configure probe for the per-filesystem sync API; it compiles and often lightly invokes `syncfs`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; defines `main`; calls `open`, `unlink`, `syncfs`, `close`; references constants/macros `O_RDWR`, `O_CREAT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value error handling uses a compact cleanup label so opened descriptors or mappings are released before returning failure.

State and persistence behavior: uses temporary filesystem objects and file descriptors, usually unlinking the name after opening so data should not persist after close.

Dependencies and integration points: depends on headers `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; preprocessor availability gates such as `#if defined(__FreeBSD_kernel__)`, `#error syncfs is not implemented with FreeBSD kernel`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syncfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syscall.c -->
# sources/test-tools/stress-ng/test/test-syscall.c

Purpose: minimal stress-ng configure probe for `syscall`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/syscall.h`, `unistd.h`; defines `main`; calls `syscall`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value direct syscall paths use `__NR_getpid` through `syscall()`.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/syscall.h`, `unistd.h`; architecture syscall numbers `__NR_getpid`; preprocessor availability gates such as `#if defined(__NR_getpid)`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: direct syscall-number probes are kernel/libc/architecture sensitive and may compile while returning `ENOSYS`, `EINVAL`, or permission errors at runtime. Test signals are successful compilation; successful linking; the expected syscall symbol being present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sysinfo.c -->
# sources/test-tools/stress-ng/test/test-sysinfo.c

Purpose: minimal stress-ng configure probe for `sysinfo`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/sysinfo.h`; uses types `struct sysinfo`; defines `main`; calls `sysinfo`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/sysinfo.h`; preprocessor availability gates such as `#if defined(__sun__)`, `#error this is not the sysinfo you are looking for`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sysinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-target-clones.c -->
# sources/test-tools/stress-ng/test/test-target-clones.c

Purpose: minimal stress-ng configure probe for `target-clones`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `features.h`, `../core-version.h`; defines `have_target_clones`, `main`; calls `NEED_GNUC`, `NEED_CLANG`, `target_clones`.

Control flow: helper definitions `have_target_clones` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `features.h`, `../core-version.h`; preprocessor availability gates such as `#if (defined(__GNUC__) &&	\`, `#if defined(__x86_64__) ||	\`, `#error arch not supported`, `#error target clones attribute not supported`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-target-clones.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcdrain.c -->
# sources/test-tools/stress-ng/test/test-tcdrain.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `tcdrain`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `termios.h`, `unistd.h`; defines `main`; calls `tcdrain`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `termios.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcdrain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcflow.c -->
# sources/test-tools/stress-ng/test/test-tcflow.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `tcflow`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `termios.h`, `unistd.h`; defines `main`; calls `tcflow`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `termios.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcflush.c -->
# sources/test-tools/stress-ng/test/test-tcflush.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `tcflush`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `termios.h`, `unistd.h`; defines `main`; calls `tcflush`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `termios.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcgetattr.c -->
# sources/test-tools/stress-ng/test/test-tcgetattr.c

Purpose: minimal stress-ng configure probe for the termios terminal-control API; it compiles and often lightly invokes `tcgetattr`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `termios.h`, `unistd.h`; uses types `struct termios`; defines `main`; calls `tcgetattr`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `termios.h`, `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tcgetattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tee.c -->
# sources/test-tools/stress-ng/test/test-tee.c

Purpose: minimal stress-ng configure probe for the pipe tee API; it compiles and often lightly invokes `tee`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `fcntl.h`; defines `main`; calls `tee`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-termios.c -->
# sources/test-tools/stress-ng/test/test-termios.c

Purpose: compile-time availability probe for `struct termios` associated with `termios`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/termios.h`; uses types `struct termios`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/termios.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-termios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tgkill.c -->
# sources/test-tools/stress-ng/test/test-tgkill.c

Purpose: minimal stress-ng configure probe for `tgkill`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `signal.h`; defines `main`; calls `tgkill`; references constants/macros `SIGCONT`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `signal.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tgkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-time.c -->
# sources/test-tools/stress-ng/test/test-time.c

Purpose: minimal stress-ng configure probe for `time`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `time.h`; defines `main`; calls `time`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-create.c -->
# sources/test-tools/stress-ng/test/test-timer-create.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-create`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `signal.h`, `time.h`; uses types `struct sigevent`; defines `main`; calls `timer_create`, `clock_settime`; references constants/macros `SIGEV_SIGNAL`, `SIGRTMIN`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a POSIX timer object whose expiration state lives only until deletion/process exit.

Dependencies and integration points: depends on headers `signal.h`, `time.h`; preprocessor availability gates such as `#if defined(CLOCK_REALTIME)`, `#error no POSIX clock types CLOCK_REALTIME or CLOCK_MONOTONIC`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-delete.c -->
# sources/test-tools/stress-ng/test/test-timer-delete.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-delete`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`; defines `main`; calls `timer_delete`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-delete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-getoverrun.c -->
# sources/test-tools/stress-ng/test/test-timer-getoverrun.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-getoverrun`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`; defines `main`; calls `timer_getoverrun`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-getoverrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-gettime.c -->
# sources/test-tools/stress-ng/test/test-timer-gettime.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-gettime`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`; uses types `struct itimerspec`; defines `main`; calls `timer_gettime`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-settime.c -->
# sources/test-tools/stress-ng/test/test-timer-settime.c

Purpose: minimal stress-ng configure probe for the POSIX timer API; it compiles and often lightly invokes `timer-settime`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `time.h`; uses types `struct itimerspec`; defines `main`; calls `timer_settime`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timer-settime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-create.c -->
# sources/test-tools/stress-ng/test/test-timerfd-create.c

Purpose: minimal stress-ng configure probe for the timerfd API; it compiles and often lightly invokes `timerfd-create`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/timerfd.h`; defines `main`; calls `timerfd_create`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: creates a timer file descriptor whose expiration state lives only until close/process exit.

Dependencies and integration points: depends on headers `sys/timerfd.h`; preprocessor availability gates such as `#if defined(CLOCK_REALTIME)`, `#error no POSIX clock types CLOCK_REALTIME or CLOCK_MONOTONIC`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: explicit preprocessor exclusions intentionally convert unsupported platforms into compile failures, which is the expected configure signal. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-gettime.c -->
# sources/test-tools/stress-ng/test/test-timerfd-gettime.c

Purpose: minimal stress-ng configure probe for the timerfd API; it compiles and often lightly invokes `timerfd-gettime`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/timerfd.h`; uses types `struct itimerspec`; defines `main`; calls `timerfd_gettime`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/timerfd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; expected errno paths such as `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-settime.c -->
# sources/test-tools/stress-ng/test/test-timerfd-settime.c

Purpose: minimal stress-ng configure probe for the timerfd API; it compiles and often lightly invokes `timerfd-settime`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/timerfd.h`; uses types `struct itimerspec`; defines `main`; calls `timerfd_settime`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/timerfd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; expected errno paths such as `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timerfd-settime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timex.c -->
# sources/test-tools/stress-ng/test/test-timex.c

Purpose: compile-time availability probe for `struct timex` associated with `timex`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/timex.h`; uses types `struct timex`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/timex.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timezone.c -->
# sources/test-tools/stress-ng/test/test-timezone.c

Purpose: compile-time availability probe for `struct timezone` associated with `timezone`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `sys/time.h`; uses types `struct timezone`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/time.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-timezone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tpacket_req3.c -->
# sources/test-tools/stress-ng/test/test-tpacket_req3.c

Purpose: compile-time availability probe for `struct tpacket_req3` associated with `tpacket_req3`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/if_packet.h`; uses types `struct tpacket_req3`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/if_packet.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tpacket_req3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tsearch.c -->
# sources/test-tools/stress-ng/test/test-tsearch.c

Purpose: minimal stress-ng configure probe for the tree-search API; it compiles and often lightly invokes `tsearch`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `search.h`, `stdlib.h`, `string.h`; defines `cmp`, `main`; calls `tsearch`, `tdelete`.

Control flow: helper definitions `cmp` run before or from `main()` `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `search.h`, `stdlib.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: runtime failure is intentionally coarse because these files are primarily availability probes, not exhaustive behavioral tests. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-tsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ttyname.c -->
# sources/test-tools/stress-ng/test/test-ttyname.c

Purpose: minimal stress-ng configure probe for the terminal name API; it compiles and often lightly invokes `ttyname`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`; defines `main`; calls `ttyname`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ttyname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-umount2.c -->
# sources/test-tools/stress-ng/test/test-umount2.c

Purpose: minimal stress-ng configure probe for the filesystem unmount API; it compiles and often lightly invokes `umount2`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sys/mount.h`; defines `main`; calls `umount2`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/mount.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-umount2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-uname.c -->
# sources/test-tools/stress-ng/test/test-uname.c

Purpose: minimal stress-ng configure probe for `uname`; it compiles a small C program that touches the relevant declaration, constant, or libc/kernel entry point.

Important APIs/types/functions: includes `sys/utsname.h`; uses types `struct utsname`; defines `main`; calls `uname`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sys/utsname.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-uname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unimapdesc.c -->
# sources/test-tools/stress-ng/test/test-unimapdesc.c

Purpose: compile-time availability probe for `struct unimapdesc` associated with `unimapdesc`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/kd.h`; uses types `struct unimapdesc`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/kd.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unimapdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unlinkat.c -->
# sources/test-tools/stress-ng/test/test-unlinkat.c

Purpose: minimal stress-ng configure probe for the unlinkat API; it compiles and often lightly invokes `unlinkat`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `unistd.h`, `fcntl.h`; defines `main`; calls `unlinkat`; references constants/macros `AT_FDCWD`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `unistd.h`, `fcntl.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unlinkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unshare.c -->
# sources/test-tools/stress-ng/test/test-unshare.c

Purpose: minimal stress-ng configure probe for the namespace unshare API; it compiles and often lightly invokes `unshare`-related declarations so the build system can enable matching stressor code only when available.

Important APIs/types/functions: includes `sched.h`; defines `main`; calls `unshare`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `sched.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-unshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-usbdevfs_getdriver.c -->
# sources/test-tools/stress-ng/test/test-usbdevfs_getdriver.c

Purpose: compile-time availability probe for `struct usbdevfs_getdriver` associated with `usbdevfs_getdriver`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `linux/usbdevice_fs.h`; uses types `struct usbdevfs_getdriver`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `linux/usbdevice_fs.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: the main risk is false negatives from missing development headers, old libc wrappers, unsupported kernel UAPI, or platform-specific optional definitions. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-usbdevfs_getdriver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-user-desc.c -->
# sources/test-tools/stress-ng/test/test-user-desc.c

Purpose: compile-time availability probe for `struct user_desc` associated with `user-desc`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `asm/ldt.h`, `string.h`; uses types `struct user_desc`; defines `main`; calls `memset`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `asm/ldt.h`, `string.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: architecture-specific asm header probes are intentionally nonportable. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-user-desc.c -->
