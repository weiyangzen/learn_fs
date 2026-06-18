<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h

Purpose: Declares RISC-V optimized string/memory routines and selects fortify behavior.

Important APIs/types/functions: Declares `memset`, `__memset`, `memcpy`, `__memcpy`, `memmove`, `__memmove`, `strcmp`, `strlen`, `strncmp`, `strnlen`, `strchr`, `strrchr`, and maps builtins depending on compiler/config.

Control flow: There is no inline algorithm here; calls dispatch to assembly/C implementations selected elsewhere.

State and persistence: No persistent state.

Dependencies and integration points: Used by the whole kernel, boot code, KASAN/fortify, and architecture string assembly.

Risks: Prototype or macro mismatch can bypass fortify or call unsafe overlapping copy implementations.

Test signals: LKDTM/fortify tests, KUnit string tests, boot with optimized routines, KASAN, and compiler matrix builds.

Source read size: 53 lines, 1690 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h -->
