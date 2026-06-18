# sources/distributed-fs/ceph-client/arch/arm/kernel/iwmmxt.h

Purpose: provides assembler macros and register number aliases for loading/storing iWMMXt data/control registers from assembly code.

Important APIs/types/functions: macros `wldrd`, `wldrw`, `wstrd`, and `wstrw` emit raw iWMMXt memory transfer instructions. Clang-specific `tmrc` and `tmcr` wrappers map to coprocessor 1 moves for `wCon`.

Control flow: no runtime control flow; included by `iwmmxt.S` to abstract instruction encoding.

State and persistence: no storage of its own.

Dependencies and integration: tightly coupled to iWMMXt save-area offsets and assembler capabilities. The `.irp` aliases make macro operands usable by symbolic register names such as `wR0` and `wCSSF`.

Risks: wrong encoding silently corrupts coprocessor state; macro/toolchain differences are architecture-specific. Test signals are successful ARM/Clang assembly builds and runtime iWMMXt save/restore correctness.
