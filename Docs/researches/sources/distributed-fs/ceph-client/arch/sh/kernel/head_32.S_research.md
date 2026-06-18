# sources/distributed-fs/ceph-client/arch/sh/kernel/head_32.S

Purpose: SH 32-bit boot entry code and boot-parameter page definition.

Important APIs and control flow: `boot_params_page` encodes legacy boot ABI fields such as root flags, loader type, initrd start/size, and 29/32-bit marker. `_stext` initializes SR, stack/thread-info state, optional PMB mappings, BSS clearing, optional early FDT scan, CPU initialization, synchronization, and jumps to `start_kernel`. PMB setup validates bootloader mappings, installs cached/uncached mappings by descending size, clears remaining entries, and updates uncached mapping globals when configured. `stack_start` exports boot/secondary CPU startup data consumed by SMP bring-up.

State, dependencies, and risks: persistent state is early boot params, PMB hardware state, `stack_start`, and initialized BSS. Dependencies include linker symbols, `cpu_init`, `start_kernel`, MMU/PMB register definitions, optional FDT support, and SMP secondary path. Risks are unrecoverable boot hangs from bad SR/MMU/PMB setup, wrong BSS clearing for secondary CPUs, and stale bootloader mappings. Test signals are early boot on SH2/SH3/SH4 variants, SMP secondary startup, FDT boot, and uncached mapping validation.
