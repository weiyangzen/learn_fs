
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_64.S

Purpose: 64-bit PowerPC assembly helpers for byte swapping, real-mode I/O and SCOM access on selected platforms, and kexec handoff/sequencing for SMP and Book3E/Book3S systems.

Important APIs/types/functions: `__bswapdi2`; BootX `rmci_on/off`; PMac `real_readb/real_writeb`; PA Semi `real_205_readb/real_205_writeb`; 970 `scom970_read/write`; `kexec_wait`; `kexec_smp_wait`; local `real_mode`; `kexec_sequence`; Book3E `kexec_create_tlb`; local text `kexec_flag`.

Control flow: platform real-mode I/O helpers temporarily disable data relocation or adjust HID4/SLB state, perform byte access or SCOM SPR operations, and restore MSR/HID state. `kexec_wait` loops at low thread priority until `kexec_flag` changes, then branches to the next kernel's secondary entry in real mode or via a Book3E identity TLB. `kexec_smp_wait` records real-mode kexec state in PACA and joins that loop. `kexec_sequence` switches to the kexec stack, saves arguments, disables interrupts, optionally enters real mode, copies/flushed image pages, copies the new entry stub to address zero, releases secondary CPUs, clears hash page tables if requested, and jumps to the new kernel entry with physical CPU id.

State and persistence: mutates MSR, HID4, SCOM SPRs, TLB entries, PACA kexec state, `kexec_flag`, memory at physical zero, and copied kexec image pages. This is terminal handoff state, not normal runtime persistence.

Dependencies and integration: tied to kexec core, PACA hardware CPU ids, Book3S/Book3E MMU mechanisms, `kexec_copy_flush`, `copy_and_flush`, platform CPU-frequency/early-debug configs, and ABI function descriptor handling.

Risks: terminal code has little recovery; incorrect real-mode or TLB setup can strand secondary CPUs; copying to address zero must happen after kernel data is no longer needed; endian/MSR handling matters during handoff; SCOM helpers explicitly do not check status bits.

Test signals: kexec/kdump boot cycles on Book3S and Book3E, SMP secondary release, PMac/PA Semi real-mode I/O smoke tests, 970 SCOM read/write validation, and disassembly checks under guarded configs.
