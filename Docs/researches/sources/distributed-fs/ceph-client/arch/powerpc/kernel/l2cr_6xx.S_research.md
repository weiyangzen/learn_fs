
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/l2cr_6xx.S

Purpose: low-level cache-control routines for 6xx/7xx/74xx PowerPC processors, covering L2/L3 cache configuration, global invalidation, flush-before-disable behavior, and L1 flush/disable or invalidate/enable helpers.

Important APIs/types/functions: `_set_L2CR`; `_get_L2CR`; `_set_L3CR`; `_get_L3CR`; `__flush_disable_L1`; `__inval_enable_L1`; feature fixup sections for `CPU_FTR_L2CR`, `CPU_FTR_L3CR`, `CPU_FTR_ALTIVEC`, and `CPU_FTR_SPEC7450`.

Control flow: `_set_L2CR` rejects unsupported CPUs, stops AltiVec streams, disables interrupts and data relocation, disables HID0 dynamic power management for errata, flushes existing L2 contents by reading and `dcbf`-flushing a conservative memory span, writes L2CR with invalidate/enable bits masked, performs global invalidation, waits for completion, conditionally enables L2, restores prefetch and HID0 state, then restores MSR. `_set_L3CR` performs analogous L3 disable, flush, reserved-bit/clock-enable sequencing, invalidation wait, optional enable, and MSR restore. L1 helpers sweep cache lines and toggle HID0 DCE/ICE/flash-invalidate bits.

State and persistence: persistent state is hardware cache-control SPR state, HID0/MSSCR0 bits, and actual cache contents. No software data persists beyond clobbered registers and processor cache mode.

Dependencies and integration: used by platform CPU setup, sleep/resume, CPU frequency, and board code that must manage external caches before normal C/cache APIs are safe. Depends on exact processor feature bits and SPR semantics.

Risks: wrong cache sizing or sequencing can lose dirty data or hang waiting for invalidate bits; running with MMU/interrupt state assumptions violated is unsafe; comments document errata-sensitive alignment and DPM/prefetch workarounds; 7450 bit layout differs from older L2CR users.

Test signals: only hardware or accurate emulator tests are meaningful: enable/disable L2/L3 on supported CPUs, suspend/resume or cpufreq paths, memory stress before/after toggles, and boot logs confirming feature fixups selected the intended paths.
