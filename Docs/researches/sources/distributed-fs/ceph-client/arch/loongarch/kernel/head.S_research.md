<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S

Purpose: contains the LoongArch kernel entry point and secondary CPU boot entry.
Important APIs and types: defines EFI header embedding under `CONFIG_EFI_STUB`, `kernel_entry`, image size symbols, and `smpboot_entry`.
Control flow: primary entry sets up translation/direct-map windows, switches to virtual addressing, clears BSS, saves firmware arguments, initializes percpu base and boot stack, optionally relocates/KASLR-adjusts the kernel, runs early KASAN, and calls `start_kernel`. Secondary entry performs minimal MMU/window setup, loads stack/thread info from `cpuboot_data`, and calls `start_secondary`.
State and persistence: initializes global BSS, firmware argument globals, initial stack pointer, saved SP, percpu base, and relocation-adjusted execution state.
Dependencies and integration: tied to linker symbols, EFI header, relocation code, KASAN early init, SMP boot data, `stackframe.h`, and platform firmware ABI.
Risks and test signals: early entry bugs prevent boot. Signals include EFI/non-EFI boot, relocatable/KASLR builds, SMP secondary bring-up, 4K page-size IMPCTL handling, and KASAN boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/head.S -->
