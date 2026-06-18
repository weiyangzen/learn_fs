# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-tx49xx/cpu-feature-overrides.h

Purpose: TX49xx platform CPU feature override header for Toshiba/TX49-family MIPS64 systems.

Important APIs/types/functions: Declares LL/SC and 64-bit support present, primary caches non-inclusive, and disables MIPS16, MDMX, MIPS-3D, SmartMIPS, virtual-tag I-cache, I-cache-fill-from-D-cache behavior, DSP/DSP2, MIPS MT, userlocal, and MIPS32/64 release 1/2 feature flags.

Control flow, state, and persistence: No state. The defines specialize generic MIPS code at compile time, especially CPU feature tests around atomics, cache handling, signal/FPU code, and instruction selection.

Dependencies and integration: Consumed by `cpu-features.h` and platform builds using `asm/mach-tx49xx`. Related TX49xx headers in this subset provide I/O mapping, DMA alignment, endian I/O swabbing, and virtual address layout.

Risks and test signals: Incorrectly enabling release-level features or DSP would compile instructions unsupported by older TX49 cores. Test with TX49xx defconfig builds, boot logs, atomic and cache tests, and driver I/O validation.
