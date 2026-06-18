# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/rtas-fadump.h

Purpose: Defines RTAS fadump constants, dump section layouts, register-save layouts, and utility macros shared by the RTAS fadump implementation.

Important APIs/types/functions: Provides section type constants, `RTAS_FADUMP_MIN_BOOT_MEM`, `MAX_SECTIONS`, `RTAS_FADUMP_MAX_BOOT_MEM_REGS`, `struct rtas_fadump_section`, `struct rtas_fadump_section_header`, `struct rtas_fadump_mem_struct`, register save header/entry structs, `RTAS_FADUMP_SKIP_TO_NEXT_CPU`, and CPU id mask.

Control flow: Header-only control flow is limited to the skip macro, which advances a register-entry pointer until `CPUEND` and then to the next CPU block.

State and persistence: Describes firmware-persistent dump memory structures and register-save data; it owns no runtime state.

Dependencies and integration points: Consumed by `rtas-fadump.c` and generic fadump code interacting with PAPR/RTAS firmware dump formats.

Risks: Structure packing, endian fields, and maximum section counts are firmware ABI. The skip macro assumes a valid `CPUEND` sentinel and has no bounds checking.

Test signals: Build-time layout checks, fadump registration structure inspection, active dump parsing, unknown/new section compatibility, and corrupted register-save data tests.

Source read size: 121 lines, 3930 bytes.
