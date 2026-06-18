# sources/distributed-fs/ceph-client/arch/riscv/kernel/image-vars.h

Purpose: Exposes selected kernel image symbols to decompressor/PI or EFI image-link contexts without duplicating definitions.

Important APIs/types/functions: Uses `KERNEL_MAP`/symbol alias declarations for image boundaries, EFI stub symbols, and other linker-provided addresses needed outside the normal kernel link.

Control flow: Header-only build/link metadata; no runtime control flow.

State and persistence: No mutable state. It describes persistent linker symbols.

Dependencies and integration points: Used by RISC-V image build, EFI stub, position-independent early code, and linker scripts.

Risks and test signals: Alias mistakes cause link failures or wrong runtime addresses. Test EFI and non-EFI builds, PIE/PI paths, and symbol inspection with `nm`.
