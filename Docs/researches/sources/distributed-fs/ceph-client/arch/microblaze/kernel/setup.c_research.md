# sources/distributed-fs/ceph-client/arch/microblaze/kernel/setup.c

Purpose: coordinates MicroBlaze architecture boot setup after early head code: memory setup, device-tree unflattening, CPU/cache setup, PCI init, vector copying, early clock/timer setup, and debugfs support.

Important APIs and state: per-CPU entry variables `KSP`, `KM`, `ENTRY_SP`, `R11_SAVE`, and `CURRENT_SAVE`; data-section `cmd_line`; `setup_arch()`, `machine_early_init()`, `time_init()`, optional `get_romfs_len()`, `kernel_tlb`, and debugfs initcalls.

Control flow: `setup_arch()` sets cmdline pointer, initializes memory, unflattens DT, populates CPU info, initializes caches, and probes PCI. `machine_early_init()` preserves optional romfs, clears BSS, scans DT, records kernel TLB footprint, validates MSR-instruction config, copies exception vectors from `.init.ivt` to BRAM, and initializes current per-CPU state. `time_init()` initializes OF clocks, CPU clock, and timer probe.

State and persistence: mutates boot memory limits, BSS, `klimit`, exception vector memory, per-CPU current state, and debugfs entries.

Dependencies and integration: called from `head.S`; uses `mmu_init()`, CPU-info/cache/timer/PCI subsystems, and linker symbols.

Risks and test signals: vector copy offsets and BSS clearing order are critical. ROMFS relocation can shift `klimit`. Test boot with MTD uClinux, manual reset vectors, debugfs, PCI, and MSR-instruction mismatch.
