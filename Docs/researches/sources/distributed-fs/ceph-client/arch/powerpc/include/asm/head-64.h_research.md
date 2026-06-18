# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/head-64.h

Purpose: Defines 64-bit PowerPC early exception/prolog constants, PACA slot layout, and assembly helper macros used by low-level head/exception code.

Important APIs, types, and functions: Provides `PACA_SLOT_*` offsets, `PACA_SIZE`, exception vector helper constants, `TRAMP_REAL_BEGIN`, `TRAMP_VIRT_BEGIN`, and assembly macros for fixed-size exception branches, trap vectors, KVM test bits, and label placement.

Control flow: Assembly files include these definitions to lay out early real-mode trampolines, exception vectors, and PACA references before C runtime is available.

State and persistence: No C state is stored. The constants define boot-time and exception-time memory layout that remains ABI-like for assembly.

Dependencies and integration points: Integrates with `head_64.S`, exception vector code, PACA definitions, KVM interrupt paths, and linker layout.

Risks: Any offset or vector-size mismatch can break boot or exception dispatch. Macros are sensitive to instruction size, alignment, and whether code executes in real or virtual mode.

Test signals: PPC64 boot on hash/radix platforms, exception vector entry for system reset/machine check/interrupts, KVM-enabled builds, and objdump checks for expected vector placement.
