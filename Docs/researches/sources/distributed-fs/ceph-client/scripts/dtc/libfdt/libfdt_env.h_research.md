# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/libfdt_env.h

Purpose: environment abstraction for libfdt integer types, standard includes, optional sparse annotations, and endian conversion primitives.

Important APIs/types/macros: includes `stdbool.h`, `stddef.h`, `stdint.h`, `stdlib.h`, `string.h`, and `limits.h`. Defines `FDT_FORCE` and `FDT_BITWISE` for sparse `__CHECKER__` builds. Typedefs `fdt16_t`, `fdt32_t`, and `fdt64_t` as bitwise-qualified fixed-width integer types. Provides inline `fdt16_to_cpu`, `cpu_to_fdt16`, `fdt32_to_cpu`, `cpu_to_fdt32`, `fdt64_to_cpu`, and `cpu_to_fdt64` using byte extraction.

Control flow/state: no persistent state. Conversion macros operate by reading bytes of the native integer representation, producing big-endian FDT values and vice versa.

Dependencies/integration: included by `libfdt.h` before `fdt.h` and directly by libfdt C files. It is the portability layer for endian and type behavior.

Risks: byte extraction assumes object representation access through `uint8_t *`, which is standard-friendly for byte inspection. Sparse annotations are no-ops outside checker builds, so type misuse is only caught in specialized analysis.

Test signals: endian conversions on little- and big-endian hosts, sparse builds, fixed-width type availability, and inclusion ordering before raw FDT structs.
