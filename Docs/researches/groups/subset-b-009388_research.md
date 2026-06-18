# subset-b-009388 research

This grouped report covers 256 small stress-ng configure probes under `sources/test-tools/stress-ng/test`. Each section preserves the original source path and is intended for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc32_data16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data16`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data16`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC32_DATA16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data16.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data32.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc32_data32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data32`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data32`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC32_DATA32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data32.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc32_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data8`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC32_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data8.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc32_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc64_data16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data16`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data16`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC64_DATA16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data16.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data32.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc64_data32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data32`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data32`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC64_DATA32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data32.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data64.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc64_data64.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data64`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data64`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data64`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC64_DATA64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data64.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc64_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data8`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC64_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data8.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc64_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc8_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc8_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc8_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc8_data8`. Important scalar/library types: `uint8_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc8_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC8_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc8_data8.

- Structs/types detected: uint8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc8_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ctz.c -->
# sources/test-tools/stress-ng/test/test-builtin-ctz.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_ctz`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_ctz`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_ctz`; the program returns `__builtin_ctz(argc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CTZ capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_ctz.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ctz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-expect.c -->
# sources/test-tools/stress-ng/test/test-builtin-expect.c

## Purpose

This file is a stress-ng configure test for compiler support of `LIKELY, __builtin_expect, UNLIKELY`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Local macros: `LIKELY`, `UNLIKELY`. Defined functions: `main`. Referenced calls/builtins: `LIKELY`, `__builtin_expect`, `UNLIKELY`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `LIKELY`, `__builtin_expect`, `UNLIKELY`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_EXPECT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: LIKELY, __builtin_expect, UNLIKELY.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-expect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabs.c -->
# sources/test-tools/stress-ng/test/test-builtin-fabs.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_fabs`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_fabs`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_fabs`; the program returns `(int)__builtin_fabs(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_FABS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_fabs.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabsf.c -->
# sources/test-tools/stress-ng/test/test-builtin-fabsf.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_fabsf`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_fabsf`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_fabsf`; the program returns `(int)__builtin_fabsf(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_FABSF capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_fabsf.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabsf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabsl.c -->
# sources/test-tools/stress-ng/test/test-builtin-fabsl.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_fabsl`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_fabsl`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_fabsl`; the program returns `(int)__builtin_fabsl(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_FABSL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_fabsl.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-fabsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movntdq.c -->
# sources/test-tools/stress-ng/test/test-builtin-ia32_movntdq.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_ia32_movntdq`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `xmmintrin.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_ia32_movntdq`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_ia32_movntdq`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `xmmintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms; SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_IA32_MOVNTDQ capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: xmmintrin.h.

- Calls/builtins detected: __builtin_ia32_movntdq.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movntdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movnti.c -->
# sources/test-tools/stress-ng/test/test-builtin-ia32_movnti.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_ia32_movnti`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `xmmintrin.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_ia32_movnti`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_ia32_movnti`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `xmmintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_IA32_MOVNTI capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: xmmintrin.h.

- Calls/builtins detected: __builtin_ia32_movnti.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movnti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movnti64.c -->
# sources/test-tools/stress-ng/test/test-builtin-ia32_movnti64.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_ia32_movnti64`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `xmmintrin.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_ia32_movnti64`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_ia32_movnti64`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `xmmintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_IA32_MOVNTI64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: xmmintrin.h.

- Calls/builtins detected: __builtin_ia32_movnti64.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-ia32_movnti64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-llabs.c -->
# sources/test-tools/stress-ng/test/test-builtin-llabs.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_llabs`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_llabs`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_llabs`; the program returns `(int)__builtin_llabs(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_LLABS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_llabs.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-llabs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memcmp.c -->
# sources/test-tools/stress-ng/test/test-builtin-memcmp.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_memcmp`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_memcmp`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_memcmp`; the program returns `__builtin_memcmp(&dst, &src, sizeof(dst))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_MEMCMP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_memcmp.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memcpy.c -->
# sources/test-tools/stress-ng/test/test-builtin-memcpy.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_memcpy`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_memcpy`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_memcpy`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_MEMCPY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_memcpy.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memmove.c -->
# sources/test-tools/stress-ng/test/test-builtin-memmove.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_memmove`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_memmove`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_memmove`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_MEMMOVE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_memmove.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memset.c -->
# sources/test-tools/stress-ng/test/test-builtin-memset.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_memset`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_memset`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_memset`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_MEMSET capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_memset.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-nontemporal-load.c -->
# sources/test-tools/stress-ng/test/test-builtin-nontemporal-load.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_nontemporal_load`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_nontemporal_load`. Important scalar/library types: `__uint128_t`, `uint64_t`, `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_nontemporal_load`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_NONTEMPORAL_LOAD capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 35 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_nontemporal_load.

- Structs/types detected: __uint128_t, uint64_t, uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-nontemporal-load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-nontemporal-store.c -->
# sources/test-tools/stress-ng/test/test-builtin-nontemporal-store.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_nontemporal_store`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_nontemporal_store`. Important scalar/library types: `__uint128_t`, `uint64_t`, `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_nontemporal_store`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_NONTEMPORAL_STORE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_nontemporal_store.

- Structs/types detected: __uint128_t, uint64_t, uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-nontemporal-store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-parity.c -->
# sources/test-tools/stress-ng/test/test-builtin-parity.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_parity`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_parity`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_parity`; the program returns `__builtin_parity(argc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_PARITY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_parity.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-parity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcount.c -->
# sources/test-tools/stress-ng/test/test-builtin-popcount.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_popcount`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_popcount`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_popcount`; the program returns `__builtin_popcount(argc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_POPCOUNT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 24 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_popcount.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcountl.c -->
# sources/test-tools/stress-ng/test/test-builtin-popcountl.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_popcountl`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_popcountl`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_popcountl`; the program returns `__builtin_popcountl((unsigned long int)argc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_POPCOUNTL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 24 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_popcountl.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcountl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcountll.c -->
# sources/test-tools/stress-ng/test/test-builtin-popcountll.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_popcountll`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_popcountll`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_popcountll`; the program returns `__builtin_popcountll((unsigned long long int)argc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_POPCOUNTLL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 24 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_popcountll.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-popcountll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-prefetch.c -->
# sources/test-tools/stress-ng/test/test-builtin-prefetch.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_prefetch`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_prefetch`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_prefetch`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_PREFETCH capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_prefetch.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc16_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc16_data8`. Important scalar/library types: `uint16_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc16_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC16_DATA16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc16_data8.

- Structs/types detected: uint16_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc16_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc16_data8`. Important scalar/library types: `uint16_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc16_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC16_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc16_data8.

- Structs/types detected: uint16_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc16_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data16`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data16`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC32_DATA16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data16.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data32.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data32`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data32`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC32_DATA32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data32.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc32_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc32_data8`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc32_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC32_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc32_data8.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc32_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data16`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data16`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC64_DATA16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data16.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data32.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data32`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data32`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC64_DATA32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data32.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data64.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data64.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data64`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data64`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data64`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC64_DATA64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data64.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data8`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC64_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data8.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc64_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc8_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rev_crc8_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc8_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc8_data8`. Important scalar/library types: `uint8_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc8_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_REV_CRC8_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc8_data8.

- Structs/types detected: uint8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rev_crc8_data8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rint.c -->
# sources/test-tools/stress-ng/test/test-builtin-rint.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rint`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rint`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rint`; the program returns `(int)__builtin_rint(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_RINT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_rint.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rintl.c -->
# sources/test-tools/stress-ng/test/test-builtin-rintl.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rintl`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `math.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rintl`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rintl`; the program returns `(int)__builtin_rintl(x)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_RINTL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: math.h.

- Calls/builtins detected: __builtin_rintl.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rintl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft16.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateleft16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateleft16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateleft16`. Important scalar/library types: `uint16_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateleft16`; the program returns `(int)__builtin_rotateleft16(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATELEFT16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateleft16.

- Structs/types detected: uint16_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft32.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateleft32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateleft32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateleft32`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateleft32`; the program returns `(int)__builtin_rotateleft32(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATELEFT32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateleft32.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft64.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateleft64.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateleft64`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateleft64`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateleft64`; the program returns `(int)__builtin_rotateleft64(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATELEFT64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateleft64.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateleft8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateleft8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateleft8`. Important scalar/library types: `uint8_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateleft8`; the program returns `(int)__builtin_rotateleft8(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATELEFT8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateleft8.

- Structs/types detected: uint8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateleft8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright16.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateright16.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateright16`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateright16`. Important scalar/library types: `uint16_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateright16`; the program returns `(int)__builtin_rotateright16(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATERIGHT16 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateright16.

- Structs/types detected: uint16_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright32.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateright32.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateright32`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateright32`. Important scalar/library types: `uint32_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateright32`; the program returns `(int)__builtin_rotateright32(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATERIGHT32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateright32.

- Structs/types detected: uint32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright64.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateright64.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateright64`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateright64`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateright64`; the program returns `(int)__builtin_rotateright64(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATERIGHT64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateright64.

- Structs/types detected: uint64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright8.c -->
# sources/test-tools/stress-ng/test/test-builtin-rotateright8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_rotateright8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_rotateright8`. Important scalar/library types: `uint8_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_rotateright8`; the program returns `(int)__builtin_rotateright8(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_ROTATERIGHT8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_rotateright8.

- Structs/types detected: uint8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-rotateright8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-sfence.c -->
# sources/test-tools/stress-ng/test/test-builtin-sfence.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_ia32_sfence`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_ia32_sfence`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_ia32_sfence`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_SFENCE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_ia32_sfence.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-sfence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-shuffle.c -->
# sources/test-tools/stress-ng/test/test-builtin-shuffle.c

## Purpose

This file is a stress-ng configure test for compiler support of `VEC_ELEMENTS, __attribute__, vector_size, memcpy`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`, `string.h`. Local macros: `VEC_ELEMENTS`. Defined functions: `main`. Referenced calls/builtins: `VEC_ELEMENTS`, `__attribute__`, `vector_size`, `memcpy`, `__builtin_shuffle`. Important scalar/library types: `uint64_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `VEC_ELEMENTS`, `__attribute__`, `vector_size`, `memcpy`, `__builtin_shuffle`; the program returns `(int)xsum` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`, `string.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_SHUFFLE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 49 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h, string.h.

- Calls/builtins detected: VEC_ELEMENTS, __attribute__, vector_size, memcpy, __builtin_shuffle.

- Structs/types detected: uint64_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-shuffle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-strdup.c -->
# sources/test-tools/stress-ng/test/test-builtin-strdup.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_strdup, free`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_strdup`, `free`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `__builtin_strdup`, `free`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_STRDUP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdlib.h.

- Calls/builtins detected: __builtin_strdup, free.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-strdup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-supports.c -->
# sources/test-tools/stress-ng/test/test-builtin-supports.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_cpu_supports`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_cpu_supports`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_cpu_supports`; the program returns `__builtin_cpu_supports("avx")` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_SUPPORTS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 23 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_cpu_supports.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-supports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-thread-pointer.c -->
# sources/test-tools/stress-ng/test/test-builtin-thread-pointer.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_thread_pointer`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_thread_pointer`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_thread_pointer`; the program returns `*ptr` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_THREAD_POINTER capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_thread_pointer.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-thread-pointer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_left.c -->
# sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_left.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_stdc_rotate_left`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_stdc_rotate_left`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_stdc_rotate_left`; the program returns `(int)__builtin_stdc_rotate_left(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_STDC_ROTATE_LEFT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_stdc_rotate_left.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_left.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_right.c -->
# sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_right.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_stdc_rotate_right`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Defined functions: `main`. Referenced calls/builtins: `__builtin_stdc_rotate_right`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_stdc_rotate_right`; the program returns `(int)__builtin_stdc_rotate_right(x, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_STDC_ROTATE_RIGHT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: none.

- Calls/builtins detected: __builtin_stdc_rotate_right.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin_stdc_rotate_right.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cacheflush.c -->
# sources/test-tools/stress-ng/test/test-cacheflush.c

## Purpose

This file checks that the local kernel/UAPI headers expose `cacheflush` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `asm/cachectl.h`. Defined functions: `main`. Referenced calls/builtins: `cacheflush`.

## Control Flow

Control flow is deliberately linear: `main` invokes `cacheflush`; the program returns `cacheflush(buffer, 64, 1)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `asm/cachectl.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CACHEFLUSH capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: asm/cachectl.h.

- Calls/builtins detected: cacheflush.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cap.c -->
# sources/test-tools/stress-ng/test/test-cap.c

## Purpose

This file is a portable configure probe for `getpid, capget`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/capability.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getpid`, `capget`. Important structs/unions/enums: `__user_cap_data_struct`, `__user_cap_header_struct`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getpid`, `capget`; the program returns `capget(&uch, &ucd)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/capability.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CAP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, sys/capability.h.

- Calls/builtins detected: getpid, capget.

- Structs/types detected: struct __user_cap_data_struct, struct __user_cap_header_struct.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_blk.c -->
# sources/test-tools/stress-ng/test/test-cdrom_blk.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_blk` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_blk`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(b)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_BLK capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_blk.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_blk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_mcn.c -->
# sources/test-tools/stress-ng/test/test-cdrom_mcn.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_mcn` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_mcn`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(mcn)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_MCN capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_mcn.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_mcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_msf.c -->
# sources/test-tools/stress-ng/test/test-cdrom_msf.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_msf` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_msf`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(msf)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_MSF capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_msf.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_msf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_read_audio.c -->
# sources/test-tools/stress-ng/test/test-cdrom_read_audio.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_read_audio` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_read_audio`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(ra)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_READ_AUDIO capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_read_audio.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_read_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_subchnl.c -->
# sources/test-tools/stress-ng/test/test-cdrom_subchnl.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_subchnl` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_subchnl`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(s)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_SUBCHNL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_subchnl.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_subchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_ti.c -->
# sources/test-tools/stress-ng/test/test-cdrom_ti.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_ti` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_ti`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(ti)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_TI capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_ti.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_tocentry.c -->
# sources/test-tools/stress-ng/test/test-cdrom_tocentry.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_tocentry` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_tocentry`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(entry)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_TOCENTRY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_tocentry.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_tocentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_tochdr.c -->
# sources/test-tools/stress-ng/test/test-cdrom_tochdr.c

## Purpose

This file checks that the local kernel/UAPI headers expose `memset` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`, `string.h`. Defined functions: `main`. Referenced calls/builtins: `memset`. Important structs/unions/enums: `cdrom_tochdr`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`; the program returns `sizeof(struct cdrom_tochdr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`, `string.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CDROM_TOCHDR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h, string.h.

- Calls/builtins detected: memset.

- Structs/types detected: struct cdrom_tochdr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_tochdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_volctrl.c -->
# sources/test-tools/stress-ng/test/test-cdrom_volctrl.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct cdrom_volctrl` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`. Important structs/unions/enums: `cdrom_volctrl`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(v)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CDROM_VOLCTRL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: struct cdrom_volctrl.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cdrom_volctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cfgetispeed.c -->
# sources/test-tools/stress-ng/test/test-cfgetispeed.c

## Purpose

This file is a portable configure probe for `fileno, tcgetattr, cfgetispeed`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/termios.h`, `unistd.h`, `stdio.h`. Defined functions: `main`. Referenced calls/builtins: `fileno`, `tcgetattr`, `cfgetispeed`. Important structs/unions/enums: `termios`. Important scalar/library types: `speed_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `fileno`, `tcgetattr`, `cfgetispeed`; the program returns `(int)speed` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/termios.h`, `unistd.h`, `stdio.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CFGETISPEED capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/termios.h, unistd.h, stdio.h.

- Calls/builtins detected: fileno, tcgetattr, cfgetispeed.

- Structs/types detected: struct termios, speed_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cfgetispeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cfgetospeed.c -->
# sources/test-tools/stress-ng/test/test-cfgetospeed.c

## Purpose

This file is a portable configure probe for `fileno, tcgetattr, cfgetospeed`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/termios.h`, `unistd.h`, `stdio.h`. Defined functions: `main`. Referenced calls/builtins: `fileno`, `tcgetattr`, `cfgetospeed`. Important structs/unions/enums: `termios`. Important scalar/library types: `speed_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `fileno`, `tcgetattr`, `cfgetospeed`; the program returns `(int)speed` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/termios.h`, `unistd.h`, `stdio.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CFGETOSPEED capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/termios.h, unistd.h, stdio.h.

- Calls/builtins detected: fileno, tcgetattr, cfgetospeed.

- Structs/types detected: struct termios, speed_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cfgetospeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-chroot.c -->
# sources/test-tools/stress-ng/test/test-chroot.c

## Purpose

This file is a portable configure probe for `chroot`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `chroot`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `chroot`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CHROOT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h.

- Calls/builtins detected: chroot.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-chroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clearenv.c -->
# sources/test-tools/stress-ng/test/test-clearenv.c

## Purpose

This file is a portable configure probe for `clearenv`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `clearenv`.

## Control Flow

Control flow is deliberately linear: `main` invokes `clearenv`; the program returns `clearenv()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLEARENV capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: clearenv.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clearenv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-adjtime.c -->
# sources/test-tools/stress-ng/test/test-clock-adjtime.c

## Purpose

This file is a portable configure probe for `memset, clock_adjtime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `string.h`, `time.h`, `sys/timex.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `memset`, `clock_adjtime`. Important structs/unions/enums: `timex`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `memset`, `clock_adjtime`; the program returns `clock_adjtime(CLOCK_MONOTONIC, &buf)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `time.h`, `sys/timex.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_ADJTIME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: type and ABI shape probe.

- Includes: string.h, time.h, sys/timex.h.

- Calls/builtins detected: memset, clock_adjtime.

- Structs/types detected: struct timex.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-adjtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-getres.c -->
# sources/test-tools/stress-ng/test/test-clock-getres.c

## Purpose

This file is a portable configure probe for `clock_getres`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `clock_getres`. Important structs/unions/enums: `timespec`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `clock_getres`; the program returns `clock_getres(CLOCK_MONOTONIC, &res)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_GETRES capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: clock_getres.

- Structs/types detected: struct timespec.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-getres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-gettime.c -->
# sources/test-tools/stress-ng/test/test-clock-gettime.c

## Purpose

This file is a portable configure probe for `clock_gettime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `clock_gettime`. Important structs/unions/enums: `timespec`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `clock_gettime`; the program returns `clock_gettime(CLOCK_MONOTONIC, &t)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_GETTIME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: clock_gettime.

- Structs/types detected: struct timespec.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-gettime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-nanosleep.c -->
# sources/test-tools/stress-ng/test/test-clock-nanosleep.c

## Purpose

This file is a portable configure probe for `clock_nanosleep, clock_settime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `clock_nanosleep`, `clock_settime`. Important structs/unions/enums: `timespec`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `clock_nanosleep`, `clock_settime`; the program returns `clock_settime(CLOCK_MONOTONIC, 0, &req, &rem)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_NANOSLEEP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: clock_nanosleep, clock_settime.

- Structs/types detected: struct timespec.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-settime.c -->
# sources/test-tools/stress-ng/test/test-clock-settime.c

## Purpose

This file is a portable configure probe for `clock_settime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `clock_settime`. Important structs/unions/enums: `timespec`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `clock_settime`; the program returns `clock_settime(CLOCK_MONOTONIC, &t)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_SETTIME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: clock_settime.

- Structs/types detected: struct timespec.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clock-settime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clone.c -->
# sources/test-tools/stress-ng/test/test-clone.c

## Purpose

This file is a portable configure probe for `STACK_SIZE, clone_child, clone`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sched.h`, `signal.h`, `stdio.h`. Local macros: `_GNU_SOURCE`, `STACK_SIZE`. Defined functions: `clone_child`, `main`. Referenced calls/builtins: `STACK_SIZE`, `clone_child`, `clone`. Important scalar/library types: `pid_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `clone_child` initialize data or provide callbacks; `main` invokes `STACK_SIZE`, `clone_child`, `clone`; the program returns `pid` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sched.h`, `signal.h`, `stdio.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLONE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 42 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sched.h, signal.h, stdio.h.

- Calls/builtins detected: STACK_SIZE, clone_child, clone.

- Structs/types detected: pid_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-close-range.c -->
# sources/test-tools/stress-ng/test/test-close-range.c

## Purpose

This file is a portable configure probe for `close_range`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `close_range`.

## Control Flow

Control flow is deliberately linear: `main` invokes `close_range`; the program returns `close_range(0, 255, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOSE_RANGE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: close_range.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-close-range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-complex.c -->
# sources/test-tools/stress-ng/test/test-complex.c

## Purpose

This file is a portable configure probe for `the requested language/header feature`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `complex.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `complex.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_COMPLEX capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: small compiler/configuration probe.

- Includes: complex.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-complex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-consolefontdesc.c -->
# sources/test-tools/stress-ng/test/test-consolefontdesc.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct consolefontdesc` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/kd.h`. Defined functions: `main`. Important structs/unions/enums: `consolefontdesc`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(f)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/kd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_CONSOLEFONTDESC capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/kd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct consolefontdesc.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-consolefontdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-copy-file-range.c -->
# sources/test-tools/stress-ng/test/test-copy-file-range.c

## Purpose

This file is a portable configure probe for `copy_file_range`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `copy_file_range`.

## Control Flow

Control flow is deliberately linear: `main` invokes `copy_file_range`; the program returns `copy_file_range(0, NULL, 0, NULL, 1024, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_COPY_FILE_RANGE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, fcntl.h.

- Calls/builtins detected: copy_file_range.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-copy-file-range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cpu_set_t.c -->
# sources/test-tools/stress-ng/test/test-cpu_set_t.c

## Purpose

This file is a portable configure probe for `cpu_set_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sched.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Important scalar/library types: `cpu_set_t`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(cpu_set_t)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sched.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CPU_SET_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: type and ABI shape probe.

- Includes: sched.h.

- Calls/builtins detected: none.

- Structs/types detected: cpu_set_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-cpu_set_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-crypt-r.c -->
# sources/test-tools/stress-ng/test/test-crypt-r.c

## Purpose

This file is a portable configure probe for `crypt_r`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `crypt.h`. Local macros: `_XOPEN_SOURCE`, `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `crypt_r`. Important structs/unions/enums: `crypt_data`.

## Control Flow

Control flow is deliberately linear: `main` invokes `crypt_r`; the program returns `ptr != (void *)0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `crypt.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CRYPT_R capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, crypt.h.

- Calls/builtins detected: crypt_r.

- Structs/types detected: struct crypt_data.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-crypt-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-daddr_t.c -->
# sources/test-tools/stress-ng/test/test-daddr_t.c

## Purpose

This file is a portable configure probe for `daddr_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Important scalar/library types: `daddr_t`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_DADDR_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: none.

- Structs/types detected: daddr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-daddr_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-delete-module.c -->
# sources/test-tools/stress-ng/test/test-delete-module.c

## Purpose

This file checks that the local kernel/UAPI headers expose `delete_module` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/module.h`. Defined functions: `main`. Referenced calls/builtins: `delete_module`.

## Control Flow

Control flow is deliberately linear: `main` invokes `delete_module`; the program returns `delete_module("hello", 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/module.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches; runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_DELETE_MODULE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 24 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/module.h.

- Calls/builtins detected: delete_module.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-delete-module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dirent-d_type.c -->
# sources/test-tools/stress-ng/test/test-dirent-d_type.c

## Purpose

This file is a portable configure probe for `struct dirent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `dirent.h`. Defined functions: `main`. Important structs/unions/enums: `dirent`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(d.d_type)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `dirent.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_DIRENT_D_TYPE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: dirent.h.

- Calls/builtins detected: none.

- Structs/types detected: struct dirent.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dirent-d_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dm_ioctl.c -->
# sources/test-tools/stress-ng/test/test-dm_ioctl.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct dm_ioctl` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/dm-ioctl.h`. Defined functions: `main`. Important structs/unions/enums: `dm_ioctl`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(d)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/dm-ioctl.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_DM_IOCTL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/dm-ioctl.h.

- Calls/builtins detected: none.

- Structs/types detected: struct dm_ioctl.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dm_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-drand48.c -->
# sources/test-tools/stress-ng/test/test-drand48.c

## Purpose

This file is a portable configure probe for `drand48`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `drand48`.

## Control Flow

Control flow is deliberately linear: `main` invokes `drand48`; the program returns `(int)d` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_DRAND48 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: drand48.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-drand48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dup3.c -->
# sources/test-tools/stress-ng/test/test-dup3.c

## Purpose

This file is a portable configure probe for `open, dup3, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`, `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `open`, `dup3`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `dup3`, `close`; the program returns `ret` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_DUP3 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 56 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: fcntl.h, unistd.h.

- Calls/builtins detected: open, dup3, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dup3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dvd_authinfo.c -->
# sources/test-tools/stress-ng/test/test-dvd_authinfo.c

## Purpose

This file checks that the local kernel/UAPI headers expose `the requested language/header feature` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(a)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_DVD_AUTHINFO capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dvd_authinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dvd_struct.c -->
# sources/test-tools/stress-ng/test/test-dvd_struct.c

## Purpose

This file checks that the local kernel/UAPI headers expose `the requested language/header feature` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/cdrom.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(d)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/cdrom.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_DVD_STRUCT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/cdrom.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-dvd_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-eigen.cpp -->
# sources/test-tools/stress-ng/test/test-eigen.cpp

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_EIGEN` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `eigen3/Eigen/Dense`. Local macros: `EIGEN_SUPPORTED`. Defined functions: `main`. Referenced calls/builtins: `eigen_build_test`, `Random`, `inverse`, `determinant`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `eigen_build_test`, `Random`, `inverse`, `determinant`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `eigen3/Eigen/Dense`; a C++ compiler and Eigen headers under `eigen3/Eigen/Dense`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: this is a C++ probe inside a mostly C test directory, so it depends on CXX configuration as well as CC.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_EIGEN`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 75 lines.

- Probe category: external library/header link probe.

- Includes: eigen3/Eigen/Dense.

- Calls/builtins detected: eigen_build_test, Random, inverse, determinant.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-eigen.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-endmntent.c -->
# sources/test-tools/stress-ng/test/test-endmntent.c

## Purpose

This file is a portable configure probe for `setmntent, endmntent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `mntent.h`. Defined functions: `main`. Referenced calls/builtins: `setmntent`, `endmntent`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `setmntent`, `endmntent`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `mntent.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ENDMNTENT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdio.h, mntent.h.

- Calls/builtins detected: setmntent, endmntent.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-endmntent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-endpwent.c -->
# sources/test-tools/stress-ng/test/test-endpwent.c

## Purpose

This file is a portable configure probe for `setpwent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `pwd.h`. Defined functions: `main`. Referenced calls/builtins: `setpwent`.

## Control Flow

Control flow is deliberately linear: `main` invokes `setpwent`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `pwd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ENDPWENT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, pwd.h.

- Calls/builtins detected: setpwent.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-endpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-epoll-create.c -->
# sources/test-tools/stress-ng/test/test-epoll-create.c

## Purpose

This file is a portable configure probe for `epoll_create`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/epoll.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `epoll_create`.

## Control Flow

Control flow is deliberately linear: `main` invokes `epoll_create`; the program returns `epoll_create(10)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/epoll.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_EPOLL_CREATE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/epoll.h.

- Calls/builtins detected: epoll_create.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-epoll-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-epoll-create1.c -->
# sources/test-tools/stress-ng/test/test-epoll-create1.c

## Purpose

This file is a portable configure probe for `epoll_create1`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/epoll.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `epoll_create1`.

## Control Flow

Control flow is deliberately linear: `main` invokes `epoll_create1`; the program returns `epoll_create1(0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/epoll.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_EPOLL_CREATE1 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/epoll.h.

- Calls/builtins detected: epoll_create1.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-epoll-create1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-eventfd.c -->
# sources/test-tools/stress-ng/test/test-eventfd.c

## Purpose

This file is a portable configure probe for `eventfd`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/eventfd.h`. Defined functions: `main`. Referenced calls/builtins: `eventfd`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `eventfd`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/eventfd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_EVENTFD capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/eventfd.h.

- Calls/builtins detected: eventfd.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-eventfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-executable_start.c -->
# sources/test-tools/stress-ng/test/test-executable_start.c

## Purpose

This file is a portable configure probe for `the requested language/header feature`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `__executable_start` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are the host libc/compiler declaration set. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_EXECUTABLE_START capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: small compiler/configuration probe.

- Includes: none.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-executable_start.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-execveat.c -->
# sources/test-tools/stress-ng/test/test-execveat.c

## Purpose

This file is a portable configure probe for `syscall`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`, `sys/syscall.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `syscall`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `syscall`; the program returns `syscall(__NR_execveat, 0, "/proc/self/exe", argv_new, env_new, AT_EMPTY_PATH)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`, `sys/syscall.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_EXECVEAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, fcntl.h, sys/syscall.h.

- Calls/builtins detected: syscall.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-execveat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-faccessat.c -->
# sources/test-tools/stress-ng/test/test-faccessat.c

## Purpose

This file is a portable configure probe for `faccessat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`, `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `faccessat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `faccessat`; the program returns `faccessat(AT_FDCWD, "dummytestfile", F_OK, AT_SYMLINK_NOFOLLOW)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FACCESSAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: fcntl.h, unistd.h.

- Calls/builtins detected: faccessat.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-faccessat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-faccessat2.c -->
# sources/test-tools/stress-ng/test/test-faccessat2.c

## Purpose

This file is a portable configure probe for `faccessat2`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`, `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `faccessat2`.

## Control Flow

Control flow is deliberately linear: `main` invokes `faccessat2`; the program returns `faccessat2(AT_FDCWD, "dummytestfile", F_OK, AT_SYMLINK_NOFOLLOW)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FACCESSAT2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: fcntl.h, unistd.h.

- Calls/builtins detected: faccessat2.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-faccessat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fallocate.c -->
# sources/test-tools/stress-ng/test/test-fallocate.c

## Purpose

This file is a portable configure probe for `fallocate`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `fallocate`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fallocate`; the program returns `fallocate(0, 0, 0, 4096)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FALLOCATE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: fcntl.h.

- Calls/builtins detected: fallocate.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fallocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fanotify.c -->
# sources/test-tools/stress-ng/test/test-fanotify.c

## Purpose

This file is a portable configure probe for `BUFFER_SIZE, posix_memalign, fanotify_init, free`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`, `unistd.h`, `stdlib.h`, `mntent.h`, `sys/select.h`, `sys/fanotify.h`. Local macros: `BUFFER_SIZE`. Defined functions: `main`, `if`, `FAN_EVENT_OK`. Referenced calls/builtins: `BUFFER_SIZE`, `posix_memalign`, `fanotify_init`, `free`, `fanotify_mark`, `read`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `close`. Important structs/unions/enums: `fanotify_event_metadata`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if`, `FAN_EVENT_OK` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `BUFFER_SIZE`, `posix_memalign`, `fanotify_init`, `free`, `fanotify_mark`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`, `unistd.h`, `stdlib.h`, `mntent.h`, `sys/select.h`, `sys/fanotify.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FANOTIFY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 106 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: fcntl.h, unistd.h, stdlib.h, mntent.h, sys/select.h, sys/fanotify.h.

- Calls/builtins detected: BUFFER_SIZE, posix_memalign, fanotify_init, free, fanotify_mark, read, FAN_EVENT_OK, FAN_EVENT_NEXT, close.

- Structs/types detected: struct fanotify_event_metadata, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fanotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchmodat.c -->
# sources/test-tools/stress-ng/test/test-fchmodat.c

## Purpose

This file is a portable configure probe for `fchmodat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/stat.h`. Defined functions: `main`. Referenced calls/builtins: `fchmodat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fchmodat`; the program returns `fchmodat(0, "", 0, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/stat.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FCHMODAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/stat.h.

- Calls/builtins detected: fchmodat.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchmodat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchmodat2.c -->
# sources/test-tools/stress-ng/test/test-fchmodat2.c

## Purpose

This file is a portable configure probe for `fchmodat2`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/stat.h`. Defined functions: `main`. Referenced calls/builtins: `fchmodat2`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fchmodat2`; the program returns `fchmodat2(0, "", 0, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/stat.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FCHMODAT2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/stat.h.

- Calls/builtins detected: fchmodat2.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchmodat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchownat.c -->
# sources/test-tools/stress-ng/test/test-fchownat.c

## Purpose

This file is a portable configure probe for `fchownat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `fchownat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fchownat`; the program returns `fchownat(0, "", 0, 0, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FCHOWNAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: fchownat.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fchownat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fdatasync.c -->
# sources/test-tools/stress-ng/test/test-fdatasync.c

## Purpose

This file is a portable configure probe for `open, unlink, fdatasync, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `fdatasync`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `fdatasync`, `close`; the program returns `err` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FDATASYNC capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 43 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: open, unlink, fdatasync, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fdatasync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fexecve.c -->
# sources/test-tools/stress-ng/test/test-fexecve.c

## Purpose

This file is a portable configure probe for `strcmp, open, fexecve`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`, `string.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `strcmp`, `open`, `fexecve`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `strcmp`, `open`, `fexecve`; the program returns `fexecve(fd, argv_new, env_new)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`, `string.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FEXECVE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, fcntl.h, string.h.

- Calls/builtins detected: strcmp, open, fexecve.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fexecve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fgetxattr.c -->
# sources/test-tools/stress-ng/test/test-fgetxattr.c

## Purpose

This file is a portable configure probe for `fgetxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `fgetxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fgetxattr`; the program returns `fgetxattr(fd, "name", value, sizeof(value))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FGETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: fgetxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fgetxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-finit-module.c -->
# sources/test-tools/stress-ng/test/test-finit-module.c

## Purpose

This file checks that the local kernel/UAPI headers expose `finit_module, open` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/module.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. Defined functions: `main`, `if`. Referenced calls/builtins: `finit_module`, `open`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `finit_module`, `open`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/module.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches; runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success; dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FINIT_MODULE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/module.h, sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: finit_module, open.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-finit-module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-flistxattr.c -->
# sources/test-tools/stress-ng/test/test-flistxattr.c

## Purpose

This file is a portable configure probe for `flistxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `flistxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `flistxattr`; the program returns `flistxattr(fd, list, sizeof(list))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FLISTXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: flistxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-flistxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-float.c -->
# sources/test-tools/stress-ng/test/test-float.c

## Purpose

This file is a portable configure probe for `NEED_GNUC, __attribute__, optimize, float_ops`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `math.h`, `../core-version.h`. Local macros: `OPTIMIZE3`, `OPTIMIZE3`, `float_ops`. Defined functions: `test`, `main`. Referenced calls/builtins: `NEED_GNUC`, `__attribute__`, `optimize`, `float_ops`, `_sin`, `_cos`, `test`.

## Control Flow

Control flow is deliberately linear: helper function(s) `test` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `NEED_GNUC`, `__attribute__`, `optimize`, `float_ops`, `_sin`; the program returns `(int)test()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FLOAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 69 lines.

- Probe category: small compiler/configuration probe.

- Includes: math.h, ../core-version.h.

- Calls/builtins detected: NEED_GNUC, __attribute__, optimize, float_ops, _sin, _cos, test.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-flock.c -->
# sources/test-tools/stress-ng/test/test-flock.c

## Purpose

This file is a portable configure probe for `flock`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/file.h`. Defined functions: `main`. Referenced calls/builtins: `flock`.

## Control Flow

Control flow is deliberately linear: `main` invokes `flock`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/file.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FLOCK capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/file.h.

- Calls/builtins detected: flock.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_drive_struct.c -->
# sources/test-tools/stress-ng/test/test-floppy_drive_struct.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct floppy_drive_struct` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fd.h`. Defined functions: `main`. Important structs/unions/enums: `floppy_drive_struct`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(drive)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FLOPPY_DRIVE_STRUCT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct floppy_drive_struct.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_drive_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_fdc_state.c -->
# sources/test-tools/stress-ng/test/test-floppy_fdc_state.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct floppy_fdc_state` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fd.h`. Defined functions: `main`. Important structs/unions/enums: `floppy_fdc_state`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(state)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FLOPPY_FDC_STATE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct floppy_fdc_state.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_fdc_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_struct.c -->
# sources/test-tools/stress-ng/test/test-floppy_struct.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct floppy_struct` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fd.h`. Defined functions: `main`. Important structs/unions/enums: `floppy_struct`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(floppy)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FLOPPY_STRUCT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct floppy_struct.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_write_errors.c -->
# sources/test-tools/stress-ng/test/test-floppy_write_errors.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct floppy_write_errors` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fd.h`. Defined functions: `main`. Important structs/unions/enums: `floppy_write_errors`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(errors)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FLOPPY_WRITE_ERRORS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct floppy_write_errors.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-floppy_write_errors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fremovexattr.c -->
# sources/test-tools/stress-ng/test/test-fremovexattr.c

## Purpose

This file is a portable configure probe for `fremovexattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `fremovexattr`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fremovexattr`; the program returns `fremovexattr(fd, "name")` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FREMOVEXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: fremovexattr.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fremovexattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fs_sysfs_path.c -->
# sources/test-tools/stress-ng/test/test-fs_sysfs_path.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fs_sysfs_path` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fs.h`. Defined functions: `main`. Important structs/unions/enums: `fs_sysfs_path`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(path)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fs.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FS_SYSFS_PATH capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fs.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fs_sysfs_path.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fs_sysfs_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsconfig.c -->
# sources/test-tools/stress-ng/test/test-fsconfig.c

## Purpose

This file is a portable configure probe for `fsconfig`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mount.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `fsconfig`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fsconfig`; the program returns `fsconfig(-1, 0, "key", NULL, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mount.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FSCONFIG capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mount.h.

- Calls/builtins detected: fsconfig.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsetxattr.c -->
# sources/test-tools/stress-ng/test/test-fsetxattr.c

## Purpose

This file is a portable configure probe for `fsetxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `fsetxattr`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fsetxattr`; the program returns `fsetxattr(fd, "name", value, sizeof(value), 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FSETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: fsetxattr.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsetxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsmount.c -->
# sources/test-tools/stress-ng/test/test-fsmount.c

## Purpose

This file is a portable configure probe for `fsmount`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mount.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `fsmount`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fsmount`; the program returns `fsmount(-1, 0, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mount.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FSMOUNT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mount.h.

- Calls/builtins detected: fsmount.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsopen.c -->
# sources/test-tools/stress-ng/test/test-fsopen.c

## Purpose

This file is a portable configure probe for `fsopen`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mount.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `fsopen`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fsopen`; the program returns `fsopen("example", 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mount.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FSOPEN capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mount.h.

- Calls/builtins detected: fsopen.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fstat.c -->
# sources/test-tools/stress-ng/test/test-fstat.c

## Purpose

This file is a portable configure probe for `open, fstat, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`, `if`. Referenced calls/builtins: `open`, `fstat`, `close`. Important structs/unions/enums: `stat`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `fstat`, `close`; the program returns `ret` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FSTAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/types.h, sys/stat.h, unistd.h, fcntl.h.

- Calls/builtins detected: open, fstat, close.

- Structs/types detected: struct stat.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fstatat.c -->
# sources/test-tools/stress-ng/test/test-fstatat.c

## Purpose

This file is a portable configure probe for `fstatat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sys/stat.h`, `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `fstatat`. Important structs/unions/enums: `stat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fstatat`; the program returns `fstatat(AT_FDCWD, "test", &buf, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FSTATAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: fstatat.

- Structs/types detected: struct stat.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fstatat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsuuid2.c -->
# sources/test-tools/stress-ng/test/test-fsuuid2.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fsuuid2` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fs.h`. Defined functions: `main`. Important structs/unions/enums: `fsuuid2`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(uuid)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fs.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FSUUID2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fs.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fsuuid2.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsuuid2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsverity_digest.c -->
# sources/test-tools/stress-ng/test/test-fsverity_digest.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fsverity_digest` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fsverity.h`. Defined functions: `main`. Important structs/unions/enums: `fsverity_digest`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(digest)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fsverity.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FSVERITY_DIGEST capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fsverity.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fsverity_digest.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsverity_digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsverity_enable_arg.c -->
# sources/test-tools/stress-ng/test/test-fsverity_enable_arg.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fsverity_enable_arg` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fsverity.h`. Defined functions: `main`. Important structs/unions/enums: `fsverity_enable_arg`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(enable)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fsverity.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FSVERITY_ENABLE_ARG capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fsverity.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fsverity_enable_arg.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsverity_enable_arg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsxattr.c -->
# sources/test-tools/stress-ng/test/test-fsxattr.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fsxattr` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fs.h`. Defined functions: `main`. Important structs/unions/enums: `fsxattr`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(attr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fs.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FSXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fs.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fsxattr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsync.c -->
# sources/test-tools/stress-ng/test/test-fsync.c

## Purpose

This file is a portable configure probe for `open, unlink, fsync, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `fsync`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `fsync`, `close`; the program returns `err` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FSYNC capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 43 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: open, unlink, fsync, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimens.c -->
# sources/test-tools/stress-ng/test/test-futimens.c

## Purpose

This file is a portable configure probe for `open, unlink, futimens, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `futimens`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `futimens`, `close`; the program returns `1` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FUTIMENS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 48 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/time.h, sys/types.h, sys/stat.h, fcntl.h, unistd.h.

- Calls/builtins detected: open, unlink, futimens, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimes.c -->
# sources/test-tools/stress-ng/test/test-futimes.c

## Purpose

This file is a portable configure probe for `open, unlink, futimes, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `futimes`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `futimes`, `close`; the program returns `1` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FUTIMES capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/time.h, sys/types.h, sys/stat.h, fcntl.h, unistd.h.

- Calls/builtins detected: open, unlink, futimes, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimesat.c -->
# sources/test-tools/stress-ng/test/test-futimesat.c

## Purpose

This file is a portable configure probe for `open, futimesat, unlink, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `open`, `futimesat`, `unlink`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `futimesat`, `unlink`, `close`; the program returns `1` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FUTIMESAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 42 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/time.h, sys/types.h, sys/stat.h, fcntl.h, unistd.h.

- Calls/builtins detected: open, futimesat, unlink, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-futimesat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getauxval.c -->
# sources/test-tools/stress-ng/test/test-getauxval.c

## Purpose

This file is a portable configure probe for `getauxval`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/auxv.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getauxval`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getauxval`; the program returns `getauxval(0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/auxv.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETAUXVAL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/auxv.h.

- Calls/builtins detected: getauxval.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getauxval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getcpu.c -->
# sources/test-tools/stress-ng/test/test-getcpu.c

## Purpose

This file is a portable configure probe for `getcpu`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sched.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getcpu`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getcpu`; the program returns `getcpu(&cpu, &node)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sched.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETCPU capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sched.h.

- Calls/builtins detected: getcpu.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getdomainname.c -->
# sources/test-tools/stress-ng/test/test-getdomainname.c

## Purpose

This file is a portable configure probe for `getdomainname`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getdomainname`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getdomainname`; the program returns `getdomainname(name, sizeof(name))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETDOMAINNAME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getdomainname.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getdomainname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getdtablesize.c -->
# sources/test-tools/stress-ng/test/test-getdtablesize.c

## Purpose

This file is a portable configure probe for `getdtablesize`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getdtablesize`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getdtablesize`; the program returns `getdtablesize()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETDTABLESIZE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getdtablesize.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getdtablesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getentropy.c -->
# sources/test-tools/stress-ng/test/test-getentropy.c

## Purpose

This file is a portable configure probe for `getentropy`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getentropy`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getentropy`; the program returns `getentropy(buf, sizeof(buf))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETENTROPY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getentropy.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getentropy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getexecname.c -->
# sources/test-tools/stress-ng/test/test-getexecname.c

## Purpose

This file is a portable configure probe for `getexecname`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `getexecname`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getexecname`; the program returns `name != NULL` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETEXECNAME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: getexecname.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getexecname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getgroups.c -->
# sources/test-tools/stress-ng/test/test-getgroups.c

## Purpose

This file is a portable configure probe for `getgroups`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `grp.h`. Defined functions: `main`. Referenced calls/builtins: `getgroups`. Important scalar/library types: `gid_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getgroups`; the program returns `getgroups(32, groups)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `grp.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETGROUPS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, grp.h.

- Calls/builtins detected: getgroups.

- Structs/types detected: gid_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gethostid.c -->
# sources/test-tools/stress-ng/test/test-gethostid.c

## Purpose

This file is a portable configure probe for `gethostid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `gethostid`.

## Control Flow

Control flow is deliberately linear: `main` invokes `gethostid`; the program returns `gethostid()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETHOSTID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: gethostid.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gethostid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gethostname.c -->
# sources/test-tools/stress-ng/test/test-gethostname.c

## Purpose

This file is a portable configure probe for `gethostname`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `gethostname`.

## Control Flow

Control flow is deliberately linear: `main` invokes `gethostname`; the program returns `gethostname(name, sizeof(name))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETHOSTNAME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: gethostname.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gethostname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getitimer.c -->
# sources/test-tools/stress-ng/test/test-getitimer.c

## Purpose

This file is a portable configure probe for `memset, getitimer`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `string.h`, `sys/time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `memset`, `getitimer`. Important structs/unions/enums: `itimerval`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`, `getitimer`; the program returns `getitimer(ITIMER_REAL, &old)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `sys/time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETITIMER capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: string.h, sys/time.h.

- Calls/builtins detected: memset, getitimer.

- Structs/types detected: struct itimerval.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getitimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getloadavg.c -->
# sources/test-tools/stress-ng/test/test-getloadavg.c

## Purpose

This file is a portable configure probe for `getloadavg`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getloadavg`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getloadavg`; the program returns `getloadavg(loadavg, 3)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETLOADAVG capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: getloadavg.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getloadavg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getlogin.c -->
# sources/test-tools/stress-ng/test/test-getlogin.c

## Purpose

This file is a portable configure probe for `getlogin`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getlogin`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getlogin`; the program returns `(str != NULL)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETLOGIN capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getlogin.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getlogin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getmntent.c -->
# sources/test-tools/stress-ng/test/test-getmntent.c

## Purpose

This file is a portable configure probe for `setmntent, getmntent, printf, endmntent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `mntent.h`. Defined functions: `main`. Referenced calls/builtins: `setmntent`, `getmntent`, `printf`, `endmntent`. Important structs/unions/enums: `mntent`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `setmntent`, `getmntent`, `printf`, `endmntent`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `mntent.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETMNTENT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: type and ABI shape probe.

- Includes: stdio.h, mntent.h.

- Calls/builtins detected: setmntent, getmntent, printf, endmntent.

- Structs/types detected: struct mntent.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getmntent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getmntinfo.c -->
# sources/test-tools/stress-ng/test/test-getmntinfo.c

## Purpose

This file is a portable configure probe for `getmntinfo`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/param.h`, `sys/ucred.h`, `sys/mount.h`. Defined functions: `main`. Referenced calls/builtins: `getmntinfo`. Important structs/unions/enums: `statfs`, `statvfs`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `getmntinfo`; the program returns `getmntinfo(&statbufs, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/param.h`, `sys/ucred.h`, `sys/mount.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETMNTINFO capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/param.h, sys/ucred.h, sys/mount.h.

- Calls/builtins detected: getmntinfo.

- Structs/types detected: struct statfs, struct statvfs.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getmntinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpagesize.c -->
# sources/test-tools/stress-ng/test/test-getpagesize.c

## Purpose

This file is a portable configure probe for `getpagesize`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getpagesize`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getpagesize`; the program returns `sz == 4096` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETPAGESIZE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getpagesize.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpagesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpgid.c -->
# sources/test-tools/stress-ng/test/test-getpgid.c

## Purpose

This file is a portable configure probe for `getpid, getpgid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getpid`, `getpgid`. Important scalar/library types: `pid_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getpid`, `getpgid`; the program returns `getpgid(pid)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETPGID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, unistd.h.

- Calls/builtins detected: getpid, getpgid.

- Structs/types detected: pid_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpgrp.c -->
# sources/test-tools/stress-ng/test/test-getpgrp.c

## Purpose

This file is a portable configure probe for `NEED_GLIBC, getpgrp`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `unistd.h`, `features.h`, `../core-version.h`. Defined functions: `main`. Referenced calls/builtins: `NEED_GLIBC`, `getpgrp`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `NEED_GLIBC`, `getpgrp`; the program returns `getpgrp()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `unistd.h`, `features.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETPGRP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, unistd.h, features.h, ../core-version.h.

- Calls/builtins detected: NEED_GLIBC, getpgrp.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpriority.c -->
# sources/test-tools/stress-ng/test/test-getpriority.c

## Purpose

This file is a portable configure probe for `getpriority`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/resource.h`. Defined functions: `main`. Referenced calls/builtins: `getpriority`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getpriority`; the program returns `getpriority(PRIO_USER, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/resource.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETPRIORITY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/time.h, sys/resource.h.

- Calls/builtins detected: getpriority.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpriority.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpwent.c -->
# sources/test-tools/stress-ng/test/test-getpwent.c

## Purpose

This file is a portable configure probe for `getpwent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `pwd.h`. Defined functions: `main`. Referenced calls/builtins: `getpwent`. Important structs/unions/enums: `passwd`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `getpwent`; the program returns `1` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `pwd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETPWENT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, pwd.h.

- Calls/builtins detected: getpwent.

- Structs/types detected: struct passwd.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getpwent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getrandom.c -->
# sources/test-tools/stress-ng/test/test-getrandom.c

## Purpose

This file is a portable configure probe for `getrandom`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/random.h`. Defined functions: `main`. Referenced calls/builtins: `getrandom`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getrandom`; the program returns `(int)getrandom(buf, sizeof(buf), 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/random.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_GETRANDOM capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/random.h.

- Calls/builtins detected: getrandom.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getresgid.c -->
# sources/test-tools/stress-ng/test/test-getresgid.c

## Purpose

This file is a portable configure probe for `getresgid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getresgid`. Important scalar/library types: `gid_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getresgid`; the program returns `getresgid(&rgid, &egid, &sgid)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETRESGID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getresgid.

- Structs/types detected: gid_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getresgid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getresuid.c -->
# sources/test-tools/stress-ng/test/test-getresuid.c

## Purpose

This file is a portable configure probe for `getresuid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getresuid`. Important scalar/library types: `gid_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getresuid`; the program returns `getresuid(&ruid, &euid, &suid)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETRESUID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: getresuid.

- Structs/types detected: gid_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getresuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getrusage.c -->
# sources/test-tools/stress-ng/test/test-getrusage.c

## Purpose

This file is a portable configure probe for `getrusage`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/resource.h`. Defined functions: `main`. Referenced calls/builtins: `getrusage`. Important structs/unions/enums: `rusage`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getrusage`; the program returns `getrusage(RUSAGE_SELF, &usage)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/resource.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETRUSAGE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/time.h, sys/resource.h.

- Calls/builtins detected: getrusage.

- Structs/types detected: struct rusage.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getrusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getsid.c -->
# sources/test-tools/stress-ng/test/test-getsid.c

## Purpose

This file is a portable configure probe for `getsid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `getsid`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getsid`; the program returns `getsid(0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETSID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, unistd.h.

- Calls/builtins detected: getsid.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getsid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gettid.c -->
# sources/test-tools/stress-ng/test/test-gettid.c

## Purpose

This file is a portable configure probe for `gettid`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `gettid`.

## Control Flow

Control flow is deliberately linear: `main` invokes `gettid`; the program returns `gettid()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETTID capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: gettid.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gettid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gettimeofday.c -->
# sources/test-tools/stress-ng/test/test-gettimeofday.c

## Purpose

This file is a portable configure probe for `gettimeofday`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`. Defined functions: `main`. Referenced calls/builtins: `gettimeofday`. Important structs/unions/enums: `timeval`, `timezone`.

## Control Flow

Control flow is deliberately linear: `main` invokes `gettimeofday`; the program returns `gettimeofday(&tv, &tz)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETTIMEOFDAY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/time.h.

- Calls/builtins detected: gettimeofday.

- Structs/types detected: struct timeval, struct timezone.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-gettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getxattr.c -->
# sources/test-tools/stress-ng/test/test-getxattr.c

## Purpose

This file is a portable configure probe for `getxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `getxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getxattr`; the program returns `getxattr("/path/to/somewhere", "name", value, sizeof(value))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: getxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getxattrat.c -->
# sources/test-tools/stress-ng/test/test-getxattrat.c

## Purpose

This file checks that the local kernel/UAPI headers expose `getxattrat` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`. Defined functions: `main`. Referenced calls/builtins: `getxattrat`. Important structs/unions/enums: `xattr_args`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getxattrat`; the program returns `getxattrat(AT_FDCWD, "/path/to/somewhere", 0, "name", &args, sizeof(args))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches; dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETXATTRAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: sys/types.h, fcntl.h, stddef.h, linux/xattr.h.

- Calls/builtins detected: getxattrat.

- Structs/types detected: struct xattr_args, ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-getxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-heapsort.c -->
# sources/test-tools/stress-ng/test/test-heapsort.c

## Purpose

This file is a portable configure probe for `cmpint, heapsort`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `cmpint`, `main`. Referenced calls/builtins: `cmpint`, `heapsort`.

## Control Flow

Control flow is deliberately linear: helper function(s) `cmpint` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `cmpint`, `heapsort`; the program returns `heapsort(data, 5, sizeof(int), cmpint)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_HEAPSORT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 39 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: cmpint, heapsort.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-heapsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-hsearch.c -->
# sources/test-tools/stress-ng/test/test-hsearch.c

## Purpose

This file is a portable configure probe for `hcreate, hsearch`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `search.h`, `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `hcreate`, `hsearch`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `hcreate`, `hsearch`; the program returns `(hsearch(e, ENTER) == NULL)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `search.h`, `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_HSEARCH capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: small compiler/configuration probe.

- Includes: search.h, stdlib.h.

- Calls/builtins detected: hcreate, hsearch.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-hsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si128.c -->
# sources/test-tools/stress-ng/test/test-icc-mm_stream_si128.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `_mm_stream_si128`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`. Referenced calls/builtins: `_mm_stream_si128`. Important scalar/library types: `__uint128_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `_mm_stream_si128`; the program returns `(int)val` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ICC_MM_STREAM_SI128 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 38 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: _mm_stream_si128.

- Structs/types detected: __uint128_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si32.c -->
# sources/test-tools/stress-ng/test/test-icc-mm_stream_si32.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `_mm_stream_si32`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`. Referenced calls/builtins: `_mm_stream_si32`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `_mm_stream_si32`; the program returns `val` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ICC_MM_STREAM_SI32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: _mm_stream_si32.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si64.c -->
# sources/test-tools/stress-ng/test/test-icc-mm_stream_si64.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `_mm_stream_si64`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`. Referenced calls/builtins: `_mm_stream_si64`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `_mm_stream_si64`; the program returns `(int)val` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ICC_MM_STREAM_SI64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: _mm_stream_si64.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icc-mm_stream_si64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icmphdr.c -->
# sources/test-tools/stress-ng/test/test-icmphdr.c

## Purpose

This file is a portable configure probe for `struct icmphdr, struct iphdr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `netinet/ip.h`, `netinet/ip_icmp.h`. Defined functions: `main`. Important structs/unions/enums: `icmphdr`, `iphdr`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(struct iphdr) + sizeof(struct icmphdr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `netinet/ip.h`, `netinet/ip_icmp.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_ICMPHDR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: type and ABI shape probe.

- Includes: netinet/ip.h, netinet/ip_icmp.h.

- Calls/builtins detected: none.

- Structs/types detected: struct icmphdr, struct iphdr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-icmphdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ifconf.c -->
# sources/test-tools/stress-ng/test/test-ifconf.c

## Purpose

This file is a portable configure probe for `struct ifconf`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/ioctl.h`, `net/if.h`. Defined functions: `main`. Important structs/unions/enums: `ifconf`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(ifc)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/ioctl.h`, `net/if.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_IFCONF capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: type and ABI shape probe.

- Includes: sys/ioctl.h, net/if.h.

- Calls/builtins detected: none.

- Structs/types detected: struct ifconf.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ifconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ifreq.c -->
# sources/test-tools/stress-ng/test/test-ifreq.c

## Purpose

This file is a portable configure probe for `struct ifreq`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/ioctl.h`, `net/if.h`. Defined functions: `main`. Important structs/unions/enums: `ifreq`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(ifr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/ioctl.h`, `net/if.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_IFREQ capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: type and ABI shape probe.

- Includes: sys/ioctl.h, net/if.h.

- Calls/builtins detected: none.

- Structs/types detected: struct ifreq.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ifreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ino64_t.c -->
# sources/test-tools/stress-ng/test/test-ino64_t.c

## Purpose

This file is a portable configure probe for `_FILE_OFFSET_BITS`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Local macros: `_GNU_SOURCE`, `_FILE_OFFSET_BITS`. Defined functions: `main`. Referenced calls/builtins: `_FILE_OFFSET_BITS`. Important scalar/library types: `ino64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `_FILE_OFFSET_BITS`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INO64_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: _FILE_OFFSET_BITS.

- Structs/types detected: ino64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ino64_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-inotify.c -->
# sources/test-tools/stress-ng/test/test-inotify.c

## Purpose

This file is a portable configure probe for `BUFFER_SIZE, inotify_init, inotify_add_watch, read`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/select.h`, `sys/inotify.h`. Local macros: `BUFFER_SIZE`. Defined functions: `main`, `while`. Referenced calls/builtins: `BUFFER_SIZE`, `inotify_init`, `inotify_add_watch`, `read`, `inotify_rm_watch`, `close`. Important structs/unions/enums: `inotify_event`. Important scalar/library types: `ssize_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `while` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `BUFFER_SIZE`, `inotify_init`, `inotify_add_watch`, `read`, `inotify_rm_watch`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/select.h`, `sys/inotify.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_INOTIFY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 112 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/select.h, sys/inotify.h.

- Calls/builtins detected: BUFFER_SIZE, inotify_init, inotify_add_watch, read, inotify_rm_watch, close.

- Structs/types detected: struct inotify_event, ssize_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-inotify1.c -->
# sources/test-tools/stress-ng/test/test-inotify1.c

## Purpose

This file is a portable configure probe for `inotify_init1, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/inotify.h`. Defined functions: `main`, `if`. Referenced calls/builtins: `inotify_init1`, `close`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `inotify_init1`, `close`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/inotify.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INOTIFY1 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 35 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/inotify.h.

- Calls/builtins detected: inotify_init1, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-inotify1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int128_t.c -->
# sources/test-tools/stress-ng/test/test-int128_t.c

## Purpose

This file is a portable configure probe for `NEED_GNUC`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Referenced calls/builtins: `NEED_GNUC`. Important scalar/library types: `__uint128_t`, `__int128_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `NEED_GNUC`.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT128_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: NEED_GNUC.

- Structs/types detected: __uint128_t, __int128_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int128_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast16_t.c -->
# sources/test-tools/stress-ng/test/test-int_fast16_t.c

## Purpose

This file is a portable configure probe for `uint_fast16_t, int_fast16_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Important scalar/library types: `uint_fast16_t`, `int_fast16_t`.

## Control Flow

Control flow is deliberately linear: `main` declares or sizes the target type and returns a constant or `sizeof` value.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT_FAST16_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: none.

- Structs/types detected: uint_fast16_t, int_fast16_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast16_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast32_t.c -->
# sources/test-tools/stress-ng/test/test-int_fast32_t.c

## Purpose

This file is a portable configure probe for `uint_fast32_t, int_fast32_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Important scalar/library types: `uint_fast32_t`, `int_fast32_t`.

## Control Flow

Control flow is deliberately linear: `main` declares or sizes the target type and returns a constant or `sizeof` value.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT_FAST32_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: none.

- Structs/types detected: uint_fast32_t, int_fast32_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast32_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast64_t.c -->
# sources/test-tools/stress-ng/test/test-int_fast64_t.c

## Purpose

This file is a portable configure probe for `uint_fast64_t, int_fast64_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Important scalar/library types: `uint_fast64_t`, `int_fast64_t`.

## Control Flow

Control flow is deliberately linear: `main` declares or sizes the target type and returns a constant or `sizeof` value.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT_FAST64_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: none.

- Structs/types detected: uint_fast64_t, int_fast64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast64_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast8_t.c -->
# sources/test-tools/stress-ng/test/test-int_fast8_t.c

## Purpose

This file is a portable configure probe for `uint_fast8_t, int_fast8_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Important scalar/library types: `uint_fast8_t`, `int_fast8_t`.

## Control Flow

Control flow is deliberately linear: `main` declares or sizes the target type and returns a constant or `sizeof` value.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT_FAST8_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: none.

- Structs/types detected: uint_fast8_t, int_fast8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-int_fast8_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-io_uring_sqe_addr3.c -->
# sources/test-tools/stress-ng/test/test-io_uring_sqe_addr3.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct io_uring_sqe` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/io_uring.h`. Defined functions: `main`. Important structs/unions/enums: `io_uring_sqe`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(sqe.addr3)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/io_uring.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_IO_URING_SQE_ADDR3 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/io_uring.h.

- Calls/builtins detected: none.

- Structs/types detected: struct io_uring_sqe.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-io_uring_sqe_addr3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-iopl.c -->
# sources/test-tools/stress-ng/test/test-iopl.c

## Purpose

This file is a portable configure probe for `iopl`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/io.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `iopl`.

## Control Flow

Control flow is deliberately linear: `main` invokes `iopl`; the program returns `iopl(0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/io.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_IOPL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/io.h.

- Calls/builtins detected: iopl.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-iopl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ioport.c -->
# sources/test-tools/stress-ng/test/test-ioport.c

## Purpose

This file is a portable configure probe for `ioperm, inb, outb`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/io.h`. Local macros: `_GNU_SOURCE`, `IO_PORT`. Defined functions: `main`. Referenced calls/builtins: `ioperm`, `inb`, `outb`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `ioperm`, `inb`, `outb`; the program returns `ret` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/io.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_IOPORT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 39 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/io.h.

- Calls/builtins detected: ioperm, inb, outb.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ioport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-iphdr.c -->
# sources/test-tools/stress-ng/test/test-iphdr.c

## Purpose

This file is a portable configure probe for `struct iphdr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `netinet/ip.h`. Defined functions: `main`. Important structs/unions/enums: `iphdr`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(struct iphdr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `netinet/ip.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_IPHDR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: type and ABI shape probe.

- Includes: netinet/ip.h.

- Calls/builtins detected: none.

- Structs/types detected: struct iphdr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-iphdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ipsec-mb-init_mb_mgr_avx.c -->
# sources/test-tools/stress-ng/test/test-ipsec-mb-init_mb_mgr_avx.c

## Purpose

This file is a portable configure probe for `init_mb_mgr_avx`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `intel-ipsec-mb.h`. Defined functions: `main`. Referenced calls/builtins: `init_mb_mgr_avx`.

## Control Flow

Control flow is deliberately linear: `main` invokes `init_mb_mgr_avx`.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `intel-ipsec-mb.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_IPSEC_MB_INIT_MB_MGR_AVX capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: small compiler/configuration probe.

- Includes: intel-ipsec-mb.h.

- Calls/builtins detected: init_mb_mgr_avx.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-ipsec-mb-init_mb_mgr_avx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-itimer_which_t.c -->
# sources/test-tools/stress-ng/test/test-itimer_which_t.c

## Purpose

This file is a portable configure probe for `__itimer_which_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Important scalar/library types: `__itimer_which_t`.

## Control Flow

Control flow is deliberately linear: the program returns `(int)i` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ITIMER_WHICH_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/time.h.

- Calls/builtins detected: none.

- Structs/types detected: __itimer_which_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-itimer_which_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-judy.c -->
# sources/test-tools/stress-ng/test/test-judy.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_JUDY` and link flags `-lJudy` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `Judy.h`. Defined functions: `main`, `if`. Referenced calls/builtins: `JLI`, `JLD`, `JLG`. Important scalar/library types: `Pvoid_t`, `Word_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `JLI`, `JLD`, `JLG`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `Judy.h`; linker availability for `-lJudy`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_JUDY`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: external library/header link probe.

- Includes: unistd.h, Judy.h.

- Calls/builtins detected: JLI, JLD, JLG.

- Structs/types detected: Pvoid_t, Word_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-judy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbdiacrs.c -->
# sources/test-tools/stress-ng/test/test-kbdiacrs.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct kbdiacrs` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/kd.h`. Defined functions: `main`. Important structs/unions/enums: `kbdiacrs`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(m)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/kd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_KBDIACRS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/kd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct kbdiacrs.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbdiacrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbentry.c -->
# sources/test-tools/stress-ng/test/test-kbentry.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct kbentry` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/kd.h`. Defined functions: `main`. Important structs/unions/enums: `kbentry`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(k)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/kd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_KBENTRY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/kd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct kbentry.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbkeycode.c -->
# sources/test-tools/stress-ng/test/test-kbkeycode.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct kbkeycode` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/kd.h`. Defined functions: `main`. Important structs/unions/enums: `kbkeycode`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(k)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/kd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_KBKEYCODE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/kd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct kbkeycode.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbkeycode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbsentry.c -->
# sources/test-tools/stress-ng/test/test-kbsentry.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct kbsentry` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/kd.h`. Defined functions: `main`. Important structs/unions/enums: `kbsentry`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(m)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/kd.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_KBSENTRY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/kd.h.

- Calls/builtins detected: none.

- Structs/types detected: struct kbsentry.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kbsentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kernel_long_t.c -->
# sources/test-tools/stress-ng/test/test-kernel_long_t.c

## Purpose

This file checks that the local kernel/UAPI headers expose `__kernel_long_t` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/posix_types.h`. Defined functions: `main`. Important scalar/library types: `__kernel_long_t`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/posix_types.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_KERNEL_LONG_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/posix_types.h.

- Calls/builtins detected: none.

- Structs/types detected: __kernel_long_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kernel_long_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kernel_ulong_t.c -->
# sources/test-tools/stress-ng/test/test-kernel_ulong_t.c

## Purpose

This file checks that the local kernel/UAPI headers expose `__kernel_ulong_t` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/posix_types.h`. Defined functions: `main`. Important scalar/library types: `__kernel_ulong_t`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/posix_types.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_KERNEL_ULONG_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/posix_types.h.

- Calls/builtins detected: none.

- Structs/types detected: __kernel_ulong_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-kernel_ulong_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-key_t.c -->
# sources/test-tools/stress-ng/test/test-key_t.c

## Purpose

This file is a portable configure probe for `key_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/sem.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Important scalar/library types: `key_t`.

## Control Flow

Control flow is deliberately linear: the program returns `(int)key` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/sem.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_KEY_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: type and ABI shape probe.

- Includes: sys/sem.h.

- Calls/builtins detected: none.

- Structs/types detected: key_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-key_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-label-as-value.c -->
# sources/test-tools/stress-ng/test/test-label-as-value.c

## Purpose

This file is a portable configure probe for `the requested language/header feature`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are the host libc/compiler declaration set. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LABEL_AS_VALUE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: small compiler/configuration probe.

- Includes: none.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-label-as-value.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-landlock_rule_type.c -->
# sources/test-tools/stress-ng/test/test-landlock_rule_type.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct landlock_rule_type` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/landlock.h`. Defined functions: `main`. Important structs/unions/enums: `landlock_rule_type`.

## Control Flow

Control flow is deliberately linear: the program returns `(int)type` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/landlock.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_LANDLOCK_RULE_TYPE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/landlock.h.

- Calls/builtins detected: none.

- Structs/types detected: struct landlock_rule_type.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-landlock_rule_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-landlock_ruleset_attr.c -->
# sources/test-tools/stress-ng/test/test-landlock_ruleset_attr.c

## Purpose

This file checks that the local kernel/UAPI headers expose `memset` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `string.h`, `linux/landlock.h`. Defined functions: `main`. Referenced calls/builtins: `memset`. Important structs/unions/enums: `landlock_ruleset_attr`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`; the program returns `sizeof(attr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `linux/landlock.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LANDLOCK_RULESET_ATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: string.h, linux/landlock.h.

- Calls/builtins detected: memset.

- Structs/types detected: struct landlock_ruleset_attr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-landlock_ruleset_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lgetxattr.c -->
# sources/test-tools/stress-ng/test/test-lgetxattr.c

## Purpose

This file is a portable configure probe for `lgetxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `lgetxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lgetxattr`; the program returns `lgetxattr("/some/path/to/somewhere", "name", value, sizeof(value))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LGETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: lgetxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lgetxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libacl.c -->
# sources/test-tools/stress-ng/test/test-libacl.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_ACL` and link flags `-lacl` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `sys/acl.h`, `acl/libacl.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `sys/acl.h`, `acl/libacl.h`; linker availability for `-lacl`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_ACL`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 51 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, sys/acl.h, acl/libacl.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libaio.c -->
# sources/test-tools/stress-ng/test/test-libaio.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_AIO` and link flags `-laio` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `libaio.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `libaio.h`; linker availability for `-laio`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_AIO`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, libaio.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libbsd.c -->
# sources/test-tools/stress-ng/test/test-libbsd.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_BSD` and link flags `-lbsd` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `string.h`, `stdlib.h`, `bsd/stdlib.h`. Defined functions: `defined`, `main`. Referenced calls/builtins: `intcmp`, `memset`, `heapsort`, `mergesort`, `radixsort`.

## Control Flow

Control flow is deliberately linear: helper function(s) `defined` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `intcmp`, `memset`, `heapsort`, `mergesort`, `radixsort`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `stdlib.h`, `bsd/stdlib.h`; linker availability for `-lbsd`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_BSD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 54 lines.

- Probe category: external library/header link probe.

- Includes: string.h, stdlib.h, bsd/stdlib.h.

- Calls/builtins detected: intcmp, memset, heapsort, mergesort, radixsort.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libbsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libcrypt.c -->
# sources/test-tools/stress-ng/test/test-libcrypt.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_CRYPT` and link flags `-lcrypt` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `string.h`, `unistd.h`, `crypt.h`. Local macros: `_GNU_SOURCE`, `_XOPEN_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `memset`, `crypt_r`, `crypt`. Important structs/unions/enums: `crypt_data`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `memset`, `crypt_r`, `crypt`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `unistd.h`, `crypt.h`; linker availability for `-lcrypt`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_CRYPT`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 46 lines.

- Probe category: external library/header link probe.

- Includes: string.h, unistd.h, crypt.h.

- Calls/builtins detected: memset, crypt_r, crypt.

- Structs/types detected: struct crypt_data.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libdl.c -->
# sources/test-tools/stress-ng/test/test-libdl.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_DL` and link flags `-ldl` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `dlfcn.h`, `gnu/lib-names.h`. Defined functions: `main`. Referenced calls/builtins: `dlopen`, `dlerror`, `dlclose`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `dlopen`, `dlerror`, `dlclose`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `dlfcn.h`, `gnu/lib-names.h`; linker availability for `-ldl`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_DL`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 38 lines.

- Probe category: external library/header link probe.

- Includes: dlfcn.h, gnu/lib-names.h.

- Calls/builtins detected: dlopen, dlerror, dlclose.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libdl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libegl.c -->
# sources/test-tools/stress-ng/test/test-libegl.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_EGL` and link flags `-lEGL` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `string.h`, `EGL/egl.h`, `EGL/eglext.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `string.h`, `EGL/egl.h`, `EGL/eglext.h`; linker availability for `-lEGL`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_EGL`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 46 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, string.h, EGL/egl.h, EGL/eglext.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libegl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgbm.c -->
# sources/test-tools/stress-ng/test/test-libgbm.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_GBM` and link flags `-lgbm` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `fcntl.h`, `unistd.h`, `gbm.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `fcntl.h`, `unistd.h`, `gbm.h`; linker availability for `-lgbm`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_GBM`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, fcntl.h, unistd.h, gbm.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgles.c -->
# sources/test-tools/stress-ng/test/test-libgles.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_GLES2` and link flags `-lGLESv2` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `stdlib.h`, `GLES2/gl2.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `stdlib.h`, `GLES2/gl2.h`; linker availability for `-lGLESv2`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_GLES2`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 65 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, stdlib.h, GLES2/gl2.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgmp.c -->
# sources/test-tools/stress-ng/test/test-libgmp.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_GMP` and link flags `-lgmp` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `gmp.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `gmp.h`; linker availability for `-lgmp`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_GMP`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 44 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, gmp.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libgmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libipsec-mb.c -->
# sources/test-tools/stress-ng/test/test-libipsec-mb.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_IPSEC_MB` and link flags `-lIPSec_MB` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `intel-ipsec-mb.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `intel-ipsec-mb.h`; linker availability for `-lIPSec_MB`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_IPSEC_MB`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: external library/header link probe.

- Includes: intel-ipsec-mb.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libipsec-mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libjpeg.c -->
# sources/test-tools/stress-ng/test/test-libjpeg.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_JPEG` and link flags `-ljpeg` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `stdlib.h`, `string.h`, `jpeglib.h`. Defined functions: `main`. Referenced calls/builtins: `memset`, `jpeg_std_error`, `jpeg_create_compress`, `jpeg_stdio_dest`, `jpeg_set_defaults`, `jpeg_set_quality`, `jpeg_start_compress`, `jpeg_write_scanlines`, `jpeg_finish_compress`, `jpeg_destroy_compress`. Important structs/unions/enums: `jpeg_compress_struct`, `jpeg_error_mgr`. Important scalar/library types: `jpeg_error_mgr`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `memset`, `jpeg_std_error`, `jpeg_create_compress`, `jpeg_stdio_dest`, `jpeg_set_defaults`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `stdlib.h`, `string.h`, `jpeglib.h`; linker availability for `-ljpeg`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `HAVE_LIB_JPEG`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 56 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, stdlib.h, string.h, jpeglib.h.

- Calls/builtins detected: memset, jpeg_std_error, jpeg_create_compress, jpeg_stdio_dest, jpeg_set_defaults, jpeg_set_quality, jpeg_start_compress, jpeg_write_scanlines, jpeg_finish_compress, jpeg_destroy_compress.

- Structs/types detected: struct jpeg_compress_struct, struct jpeg_error_mgr, jpeg_error_mgr.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libjpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libkmod.c -->
# sources/test-tools/stress-ng/test/test-libkmod.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_KMOD` and link flags `-lkmod` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `libkmod.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`, `kmod_list_foreach`. Referenced calls/builtins: `kmod_new`, `kmod_module_new_from_lookup`, `kmod_list_foreach`, `kmod_module_get_module`, `kmod_module_get_name`, `kmod_module_get_initstate`, `kmod_module_get_refcnt`, `kmod_module_unref_list`. Important structs/unions/enums: `kmod_ctx`, `kmod_list`, `kmod_module`.

## Control Flow

Control flow is deliberately linear: helper function(s) `kmod_list_foreach` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `kmod_new`, `kmod_module_new_from_lookup`, `kmod_list_foreach`, `kmod_module_get_module`, `kmod_module_get_name`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `libkmod.h`; linker availability for `-lkmod`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_KMOD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 53 lines.

- Probe category: external library/header link probe.

- Includes: unistd.h, libkmod.h.

- Calls/builtins detected: kmod_new, kmod_module_new_from_lookup, kmod_list_foreach, kmod_module_get_module, kmod_module_get_name, kmod_module_get_initstate, kmod_module_get_refcnt, kmod_module_unref_list.

- Structs/types detected: struct kmod_ctx, struct kmod_list, struct kmod_module.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libkmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-liblzma.c -->
# sources/test-tools/stress-ng/test/test-liblzma.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_LZMA` and link flags `-llzma` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `lzma.h`. Defined functions: `main`. Referenced calls/builtins: `lzma_stream_decoder`, `lzma_end`. Important scalar/library types: `lzma_stream`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lzma_stream_decoder`, `lzma_end`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `lzma.h`; linker availability for `-llzma`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_LZMA`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: external library/header link probe.

- Includes: lzma.h.

- Calls/builtins detected: lzma_stream_decoder, lzma_end.

- Structs/types detected: lzma_stream.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-liblzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libmd.c -->
# sources/test-tools/stress-ng/test/test-libmd.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_MD` and link flags `-lmd` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sha2.h`, `string.h`. Defined functions: `main`. Referenced calls/builtins: `SHA256Init`, `SHA256Update`, `strlen`, `SHA256Final`. Important scalar/library types: `uint8_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `SHA256Init`, `SHA256Update`, `strlen`, `SHA256Final`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sha2.h`, `string.h`; linker availability for `-lmd`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_MD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: external library/header link probe.

- Includes: sys/types.h, sha2.h, string.h.

- Calls/builtins detected: SHA256Init, SHA256Update, strlen, SHA256Final.

- Structs/types detected: uint8_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libmpfr.c -->
# sources/test-tools/stress-ng/test/test-libmpfr.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_MPFR` and link flags `-lmpfr -lgmp` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `gmp.h`, `mpfr.h`. Defined functions: `main`. Referenced calls/builtins: `mpfr_init2`, `mpfr_const_pi`, `mpfr_set_d`, `mpfr_set_ui`, `mpfr_mul`, `mpfr_mul_ui`, `mpfr_add_ui`, `mpfr_div`, `mpfr_div_ui`, `mpfr_ui_div`, `mpfr_add`, `mpfr_prec_round`, `mpfr_cmp`, `mpfr_set`. Important scalar/library types: `mpfr_t`, `mpfr_prec_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mpfr_init2`, `mpfr_const_pi`, `mpfr_set_d`, `mpfr_set_ui`, `mpfr_mul`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `gmp.h`, `mpfr.h`; linker availability for `-lmpfr -lgmp`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_MPFR`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 58 lines.

- Probe category: external library/header link probe.

- Includes: gmp.h, mpfr.h.

- Calls/builtins detected: mpfr_init2, mpfr_const_pi, mpfr_set_d, mpfr_set_ui, mpfr_mul, mpfr_mul_ui, mpfr_add_ui, mpfr_div, mpfr_div_ui, mpfr_ui_div, mpfr_add, mpfr_prec_round, mpfr_cmp, mpfr_set, mpfr_exp, mpfr_sin, mpfr_cos, mpfr_log, mpfr_clear, mpfr_free_cache.

- Structs/types detected: mpfr_t, mpfr_prec_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libmpfr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libpthread-spinlock.c -->
# sources/test-tools/stress-ng/test/test-libpthread-spinlock.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_PTHREAD_SPINLOCK` and link flags `-lpthread` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `pthread.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `pthread.h`; linker availability for `-lpthread`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_PTHREAD_SPINLOCK`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, pthread.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libpthread-spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libpthread.c -->
# sources/test-tools/stress-ng/test/test-libpthread.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_PTHREAD` and link flags `-lpthread` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `semaphore.h`, `pthread.h`, `signal.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `semaphore.h`, `pthread.h`, `signal.h`; linker availability for `-lpthread`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_PTHREAD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 48 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, semaphore.h, pthread.h, signal.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libpthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-librt.c -->
# sources/test-tools/stress-ng/test/test-librt.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_RT` and link flags `-lrt` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `signal.h`, `time.h`, `aio.h`, `mqueue.h`, `sys/mman.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `signal.h`, `time.h`, `aio.h`, `mqueue.h`, `sys/mman.h`; linker availability for `-lrt`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_RT`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 69 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, signal.h, time.h, aio.h, mqueue.h, sys/mman.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-librt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libsctp.c -->
# sources/test-tools/stress-ng/test/test-libsctp.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_SCTP` and link flags `-lsctp` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `sys/types.h`, `sys/socket.h`, `netinet/sctp.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `sys/types.h`, `sys/socket.h`, `netinet/sctp.h`; linker availability for `-lsctp`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_SCTP`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 47 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, sys/types.h, sys/socket.h, netinet/sctp.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libsctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libxxhash.c -->
# sources/test-tools/stress-ng/test/test-libxxhash.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_XXHASH` and link flags `-lxxhash` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `xxhash.h`, `string.h`. Defined functions: `main`. Referenced calls/builtins: `XXH64`, `strlen`. Important scalar/library types: `XXH64_hash_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `XXH64`, `strlen`; the program returns `(int)hash` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `xxhash.h`, `string.h`; linker availability for `-lxxhash`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_XXHASH`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: external library/header link probe.

- Includes: xxhash.h, string.h.

- Calls/builtins detected: XXH64, strlen.

- Structs/types detected: XXH64_hash_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libxxhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libz.c -->
# sources/test-tools/stress-ng/test/test-libz.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_Z` and link flags `-lz` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `zlib.h`. Defined functions: `main`. Referenced calls/builtins: `deflateInit`, `deflateEnd`. Important scalar/library types: `z_stream`.

## Control Flow

Control flow is deliberately linear: `main` invokes `deflateInit`, `deflateEnd`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `zlib.h`; linker availability for `-lz`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_Z`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: external library/header link probe.

- Includes: zlib.h.

- Calls/builtins detected: deflateInit, deflateEnd.

- Structs/types detected: z_stream.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-libz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-linkat.c -->
# sources/test-tools/stress-ng/test/test-linkat.c

## Purpose

This file is a portable configure probe for `linkat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `linkat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `linkat`; the program returns `linkat(0, "a", 1, "b", 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LINKAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h.

- Calls/builtins detected: linkat.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-linkat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-listxattr.c -->
# sources/test-tools/stress-ng/test/test-listxattr.c

## Purpose

This file is a portable configure probe for `listxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `listxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `listxattr`; the program returns `listxattr("/some/path/to/somewhere", list, sizeof(list))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LISTXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: listxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-listxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-listxattrat.c -->
# sources/test-tools/stress-ng/test/test-listxattrat.c

## Purpose

This file is a portable configure probe for `listxattrat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `fcntl.h`. Defined functions: `main`. Referenced calls/builtins: `listxattrat`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `listxattrat`; the program returns `listxattrat(AT_FDCWD, "/some/path/to/somewhere", 0, list, sizeof(list))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LISTXATTRAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, fcntl.h.

- Calls/builtins detected: listxattrat.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-listxattrat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-llistxattr.c -->
# sources/test-tools/stress-ng/test/test-llistxattr.c

## Purpose

This file is a portable configure probe for `llistxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `llistxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `llistxattr`; the program returns `llistxattr("/some/path/to/somewhere", list, sizeof(list))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LLISTXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: llistxattr.

- Structs/types detected: ssize_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-llistxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-localtime_r.c -->
# sources/test-tools/stress-ng/test/test-localtime_r.c

## Purpose

This file is a portable configure probe for `time, localtime_r`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Defined functions: `main`. Referenced calls/builtins: `time`, `localtime_r`. Important structs/unions/enums: `tm`. Important scalar/library types: `time_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `time`, `localtime_r`; the program returns `(localtime_r(&t, &tm) != &tm)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LOCALTIME_R capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: time, localtime_r.

- Structs/types detected: struct tm, time_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-localtime_r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lockf.c -->
# sources/test-tools/stress-ng/test/test-lockf.c

## Purpose

This file is a portable configure probe for `open, unlink, lockf, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `lockf`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `lockf`, `close`; the program returns `err` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_LOCKF capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 49 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: open, unlink, lockf, close.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lockf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-loff_t.c -->
# sources/test-tools/stress-ng/test/test-loff_t.c

## Purpose

This file is a portable configure probe for `loff_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Local macros: `_GNU_SOURCE`, `_LARGEFILE_SOURCE`, `_LARGEFILE64_SOURCE`. Defined functions: `main`. Important scalar/library types: `loff_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LOFF_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: none.

- Structs/types detected: loff_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-loff_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lookup-dcookie.c -->
# sources/test-tools/stress-ng/test/test-lookup-dcookie.c

## Purpose

This file is a portable configure probe for `syscall`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/syscall.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `syscall`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `syscall`; the program returns `syscall(__NR_lookup_dcookie, buf, sizeof(buf))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/syscall.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_LOOKUP_DCOOKIE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/syscall.h.

- Calls/builtins detected: syscall.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lookup-dcookie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lrand48.c -->
# sources/test-tools/stress-ng/test/test-lrand48.c

## Purpose

This file is a portable configure probe for `lrand48`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `lrand48`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lrand48`; the program returns `(int)r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LRAND48 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: lrand48.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lrand48.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lremovexattr.c -->
# sources/test-tools/stress-ng/test/test-lremovexattr.c

## Purpose

This file is a portable configure probe for `lremovexattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `lremovexattr`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lremovexattr`; the program returns `lremovexattr("examplefile", "name")` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LREMOVEXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: lremovexattr.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lremovexattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsearch.c -->
# sources/test-tools/stress-ng/test/test-lsearch.c

## Purpose

This file is a portable configure probe for `cmp, memset, lsearch`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `search.h`, `stdlib.h`, `string.h`. Defined functions: `cmp`, `main`. Referenced calls/builtins: `cmp`, `memset`, `lsearch`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `cmp` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `cmp`, `memset`, `lsearch`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `search.h`, `stdlib.h`, `string.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LSEARCH capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 44 lines.

- Probe category: type and ABI shape probe.

- Includes: search.h, stdlib.h, string.h.

- Calls/builtins detected: cmp, memset, lsearch.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lseek64.c -->
# sources/test-tools/stress-ng/test/test-lseek64.c

## Purpose

This file is a portable configure probe for `open, lseek64, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `unistd.h`, `fcntl.h`. Local macros: `_LARGEFILE64_SOURCE`. Defined functions: `main`, `if`. Referenced calls/builtins: `open`, `lseek64`, `close`. Important scalar/library types: `off64_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `lseek64`, `close`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_LSEEK64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/types.h, unistd.h, fcntl.h.

- Calls/builtins detected: open, lseek64, close.

- Structs/types detected: off64_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lseek64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsetxattr.c -->
# sources/test-tools/stress-ng/test/test-lsetxattr.c

## Purpose

This file is a portable configure probe for `lsetxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `lsetxattr`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lsetxattr`; the program returns `lsetxattr("/some/path/to/somewhere", "name", value, sizeof(value), 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LSETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: lsetxattr.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsetxattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsm_get_self_attr.c -->
# sources/test-tools/stress-ng/test/test-lsm_get_self_attr.c

## Purpose

This file checks that the local kernel/UAPI headers expose `lsm_get_self_attr` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `stdlib.h`, `linux/lsm.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `lsm_get_self_attr`. Important structs/unions/enums: `lsm_ctx`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lsm_get_self_attr`; the program returns `lsm_get_self_attr(LSM_ATTR_CURRENT, &ctx, &size, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`, `linux/lsm.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LSM_GET_SELF_ATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: stdlib.h, linux/lsm.h.

- Calls/builtins detected: lsm_get_self_attr.

- Structs/types detected: struct lsm_ctx, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsm_get_self_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsm_list_modules.c -->
# sources/test-tools/stress-ng/test/test-lsm_list_modules.c

## Purpose

This file checks that the local kernel/UAPI headers expose `lsm_get_list_modules` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `stdint.h`, `stdlib.h`, `linux/lsm.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `lsm_get_list_modules`. Important scalar/library types: `uint64_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lsm_get_list_modules`; the program returns `lsm_get_list_modules(ids, &size, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`, `stdlib.h`, `linux/lsm.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LSM_LIST_MODULES capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: stdint.h, stdlib.h, linux/lsm.h.

- Calls/builtins detected: lsm_get_list_modules.

- Structs/types detected: uint64_t, size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lsm_list_modules.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lstat.c -->
# sources/test-tools/stress-ng/test/test-lstat.c

## Purpose

This file is a portable configure probe for `lstat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `lstat`. Important structs/unions/enums: `stat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `lstat`; the program returns `lstat("/dev/null", &buf)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sys/stat.h`, `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LSTAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, sys/stat.h, unistd.h, fcntl.h.

- Calls/builtins detected: lstat.

- Structs/types detected: struct stat.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-lstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-m128i_u.c -->
# sources/test-tools/stress-ng/test/test-m128i_u.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `the requested language/header feature`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(v)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_M128I_U capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-m128i_u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-m256i_u.c -->
# sources/test-tools/stress-ng/test/test-m256i_u.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `the requested language/header feature`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(v)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_M256I_U capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-m256i_u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-machine.c -->
# sources/test-tools/stress-ng/test/test-machine.c

## Purpose

This file is a portable configure probe for `the requested language/header feature`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Defined functions: `main`.

## Control Flow

Control flow is deliberately linear: the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are the host libc/compiler declaration set. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MACHINE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 22 lines.

- Probe category: small compiler/configuration probe.

- Includes: none.

- Calls/builtins detected: none.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-madvise.c -->
# sources/test-tools/stress-ng/test/test-madvise.c

## Purpose

This file is a portable configure probe for `madvise`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mman.h`. Defined functions: `main`. Referenced calls/builtins: `madvise`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `madvise`; the program returns `madvise(buffer, sizeof(buffer), MADV_NORMAL)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MADVISE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 80 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mman.h.

- Calls/builtins detected: madvise.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-malloc-trim.c -->
# sources/test-tools/stress-ng/test/test-malloc-trim.c

## Purpose

This file is a portable configure probe for `malloc_trim`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `malloc.h`. Defined functions: `main`. Referenced calls/builtins: `malloc_trim`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `malloc_trim`; the program returns `malloc_trim((size_t)0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `malloc.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MALLOC_TRIM capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 25 lines.

- Probe category: type and ABI shape probe.

- Includes: malloc.h.

- Calls/builtins detected: malloc_trim.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-malloc-trim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-malloc-usable-size.c -->
# sources/test-tools/stress-ng/test/test-malloc-usable-size.c

## Purpose

This file is a portable configure probe for `malloc, malloc_usable_size`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `malloc.h`. Defined functions: `main`, `if`. Referenced calls/builtins: `malloc`, `malloc_usable_size`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `malloc`, `malloc_usable_size`; the program returns `ret` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `malloc.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MALLOC_USABLE_SIZE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: small compiler/configuration probe.

- Includes: malloc.h.

- Calls/builtins detected: malloc, malloc_usable_size.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-malloc-usable-size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mallopt.c -->
# sources/test-tools/stress-ng/test/test-mallopt.c

## Purpose

This file is a portable configure probe for `mallopt`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `malloc.h`. Defined functions: `main`. Referenced calls/builtins: `mallopt`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mallopt`; the program returns `mallopt(M_MMAP_THRESHOLD, 1024*1024)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `malloc.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MALLOPT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: small compiler/configuration probe.

- Includes: malloc.h.

- Calls/builtins detected: mallopt.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mallopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mathfunc.c -->
# sources/test-tools/stress-ng/test/test-mathfunc.c

## Purpose

This file is a portable configure probe for `ptrdiff_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `math.h`, `complex.h`, `stddef.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Important scalar/library types: `ptrdiff_t`.

## Control Flow

Control flow is deliberately linear: the program returns `(ptrdiff_t)&MATHFUNC + (funcs[0] == 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`, `complex.h`, `stddef.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MATHFUNC capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: type and ABI shape probe.

- Includes: math.h, complex.h, stddef.h.

- Calls/builtins detected: none.

- Structs/types detected: ptrdiff_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mathfunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-media_device_info.c -->
# sources/test-tools/stress-ng/test/test-media_device_info.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct media_device_info` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/media.h`. Defined functions: `main`. Important structs/unions/enums: `media_device_info`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(m)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/media.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_MEDIA_DEVICE_INFO capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/media.h.

- Calls/builtins detected: none.

- Structs/types detected: struct media_device_info.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-media_device_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-memalign.c -->
# sources/test-tools/stress-ng/test/test-memalign.c

## Purpose

This file is a portable configure probe for `memalign, free`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`, `malloc.h`. Defined functions: `main`. Referenced calls/builtins: `memalign`, `free`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `memalign`, `free`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`, `malloc.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MEMALIGN capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: type and ABI shape probe.

- Includes: stdlib.h, malloc.h.

- Calls/builtins detected: memalign, free.

- Structs/types detected: size_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-memalign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-membarrier.c -->
# sources/test-tools/stress-ng/test/test-membarrier.c

## Purpose

This file checks that the local kernel/UAPI headers expose `membarrier` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/membarrier.h`. Defined functions: `main`. Referenced calls/builtins: `membarrier`.

## Control Flow

Control flow is deliberately linear: `main` invokes `membarrier`; the program returns `membarrier(MEMBARRIER_CMD_GLOBAL, 0, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/membarrier.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MEMBARRIER capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 24 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/membarrier.h.

- Calls/builtins detected: membarrier.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-membarrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-memfd-create.c -->
# sources/test-tools/stress-ng/test/test-memfd-create.c

## Purpose

This file is a portable configure probe for `memfd_create`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mman.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `memfd_create`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memfd_create`; the program returns `memfd_create("testmfd", 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MEMFD_CREATE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mman.h.

- Calls/builtins detected: memfd_create.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-memfd-create.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mergesort.c -->
# sources/test-tools/stress-ng/test/test-mergesort.c

## Purpose

This file is a portable configure probe for `cmpint, mergesort`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `cmpint`, `main`. Referenced calls/builtins: `cmpint`, `mergesort`.

## Control Flow

Control flow is deliberately linear: helper function(s) `cmpint` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `cmpint`, `mergesort`; the program returns `mergesort(data, 5, sizeof(int), cmpint)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MERGESORT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 39 lines.

- Probe category: small compiler/configuration probe.

- Includes: stdlib.h.

- Calls/builtins detected: cmpint, mergesort.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mergesort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mincore.c -->
# sources/test-tools/stress-ng/test/test-mincore.c

## Purpose

This file is a portable configure probe for `mincore`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `stdint.h`, `sys/mman.h`. Defined functions: `main`. Referenced calls/builtins: `mincore`. Important scalar/library types: `uintptr_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `mincore`; the program returns `mincore((void *)ptr, sizeof(vec), vec)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `stdint.h`, `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MINCORE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, stdint.h, sys/mman.h.

- Calls/builtins detected: mincore.

- Structs/types detected: uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mincore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mkdirat.c -->
# sources/test-tools/stress-ng/test/test-mkdirat.c

## Purpose

This file is a portable configure probe for `mkdirat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/stat.h`, `sys/types.h`, `fcntl.h`, `sys/stat.h`. Defined functions: `main`. Referenced calls/builtins: `mkdirat`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mkdirat`; the program returns `mkdirat(AT_FDCWD, "test", 0666)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/stat.h`, `sys/types.h`, `fcntl.h`, `sys/stat.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MKDIRAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/stat.h, sys/types.h, fcntl.h, sys/stat.h.

- Calls/builtins detected: mkdirat.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mkdirat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mkfifo.c -->
# sources/test-tools/stress-ng/test/test-mkfifo.c

## Purpose

This file is a portable configure probe for `mkfifo`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sys/stat.h`. Defined functions: `main`. Referenced calls/builtins: `mkfifo`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mkfifo`; the program returns `mkfifo("test", 0666)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sys/stat.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MKFIFO capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, sys/stat.h.

- Calls/builtins detected: mkfifo.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mkfifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mknod.c -->
# sources/test-tools/stress-ng/test/test-mknod.c

## Purpose

This file is a portable configure probe for `memset, mknod`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/stat.h`, `string.h`. Defined functions: `main`. Referenced calls/builtins: `memset`, `mknod`. Important scalar/library types: `dev_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`, `mknod`; the program returns `mknod("test", 0600, dev)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/stat.h`, `string.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MKNOD capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/stat.h, string.h.

- Calls/builtins detected: memset, mknod.

- Structs/types detected: dev_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mknodat.c -->
# sources/test-tools/stress-ng/test/test-mknodat.c

## Purpose

This file is a portable configure probe for `memset, mknodat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `string.h`. Defined functions: `main`. Referenced calls/builtins: `memset`, `mknodat`. Important scalar/library types: `dev_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`, `mknodat`; the program returns `mknodat(AT_FDCWD, "test", 0600, dev)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `string.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MKNODAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, sys/stat.h, fcntl.h, unistd.h, string.h.

- Calls/builtins detected: memset, mknodat.

- Structs/types detected: dev_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mknodat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlock.c -->
# sources/test-tools/stress-ng/test/test-mlock.c

## Purpose

This file is a portable configure probe for `mlock`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdint.h`, `sys/mman.h`. Defined functions: `main`. Referenced calls/builtins: `mlock`. Important scalar/library types: `uintptr_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mlock`; the program returns `mlock((void *)ptr, 4096)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`, `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MLOCK capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: stdint.h, sys/mman.h.

- Calls/builtins detected: mlock.

- Structs/types detected: uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlock2.c -->
# sources/test-tools/stress-ng/test/test-mlock2.c

## Purpose

This file is a portable configure probe for `mlock2`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `stdint.h`, `sys/mman.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `mlock2`. Important scalar/library types: `uintptr_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mlock2`; the program returns `mlock2((void *)ptr, 4096, MLOCK_ONFAULT)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `stdint.h`, `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MLOCK2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, stdint.h, sys/mman.h.

- Calls/builtins detected: mlock2.

- Structs/types detected: uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlock2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlockall.c -->
# sources/test-tools/stress-ng/test/test-mlockall.c

## Purpose

This file is a portable configure probe for `mlockall`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/mman.h`. Defined functions: `main`. Referenced calls/builtins: `mlockall`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mlockall`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MLOCKALL capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/mman.h.

- Calls/builtins detected: mlockall.

- Structs/types detected: none.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mlockall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_add_epi8.c -->
# sources/test-tools/stress-ng/test/test-mm256_add_epi8.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `rndset, __attribute__, target, _mm256_add_epi8`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`, `string.h`, `stdint.h`. Defined functions: `rndset`, `target`. Referenced calls/builtins: `rndset`, `__attribute__`, `target`, `_mm256_add_epi8`. Important scalar/library types: `size_t`, `uintptr_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `rndset`, `target` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `rndset`, `__attribute__`, `target`, `_mm256_add_epi8`; the program returns `*(int *)&r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`, `string.h`, `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MM256_ADD_EPI8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h, string.h, stdint.h.

- Calls/builtins detected: rndset, __attribute__, target, _mm256_add_epi8.

- Structs/types detected: size_t, uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_add_epi8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_dpbusd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm256_dpbusd_epi32.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `rndset, __attribute__, target, _mm256_dpbusd_epi32`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`, `string.h`, `stdint.h`. Defined functions: `rndset`, `target`. Referenced calls/builtins: `rndset`, `__attribute__`, `target`, `_mm256_dpbusd_epi32`. Important scalar/library types: `size_t`, `uintptr_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `rndset`, `target` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `rndset`, `__attribute__`, `target`, `_mm256_dpbusd_epi32`; the program returns `*(int *)&r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`, `string.h`, `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MM256_DPBUSD_EPI32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 42 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h, string.h, stdint.h.

- Calls/builtins detected: rndset, __attribute__, target, _mm256_dpbusd_epi32.

- Structs/types detected: size_t, uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_dpbusd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_dpwssd_epi32.c -->
# sources/test-tools/stress-ng/test/test-mm256_dpwssd_epi32.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `rndset, __attribute__, target, _mm256_dpwssd_epi32`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`, `string.h`, `stdint.h`. Defined functions: `rndset`, `target`. Referenced calls/builtins: `rndset`, `__attribute__`, `target`, `_mm256_dpwssd_epi32`. Important scalar/library types: `size_t`, `uintptr_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `rndset`, `target` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `rndset`, `__attribute__`, `target`, `_mm256_dpwssd_epi32`; the program returns `*(int *)&r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`, `string.h`, `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MM256_DPWSSD_EPI32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 42 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h, string.h, stdint.h.

- Calls/builtins detected: rndset, __attribute__, target, _mm256_dpwssd_epi32.

- Structs/types detected: size_t, uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_dpwssd_epi32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_loadu_si256.c -->
# sources/test-tools/stress-ng/test/test-mm256_loadu_si256.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `rndset, __attribute__, target, _mm256_loadu_si256`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`, `string.h`, `stdint.h`. Defined functions: `rndset`, `target`. Referenced calls/builtins: `rndset`, `__attribute__`, `target`, `_mm256_loadu_si256`. Important scalar/library types: `size_t`, `uintptr_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `rndset`, `target` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `rndset`, `__attribute__`, `target`, `_mm256_loadu_si256`; the program returns `*(int *)&r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`, `string.h`, `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MM256_LOADU_SI256 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h, string.h, stdint.h.

- Calls/builtins detected: rndset, __attribute__, target, _mm256_loadu_si256.

- Structs/types detected: size_t, uintptr_t.

<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-mm256_loadu_si256.c -->
