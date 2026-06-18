# sources/distributed-fs/ceph-client/arch/arm64/kernel/head.S

Purpose: Contains the low-level arm64 kernel image header, primary boot entry, secondary CPU entry, exception-level setup, MMU enabling, and handoff to C boot code.

Important symbols and routines: `primary_entry`, `record_mmu_state`, `preserve_boot_args`, `init_kernel_el`, `secondary_holding_pen`, `secondary_entry`, `secondary_startup`, `__enable_mmu`, `__primary_switch`, `__primary_switched`, and `__secondary_switched`. It emits the boot loader Image header and EFI PE header and uses the `init_cpu_task` macro to establish task, stack, frame record, shadow call stack, and per-CPU offset.

Control flow: the primary CPU records whether it entered with MMU/cache enabled, preserves x0-x3 boot args, creates an initial idmap via PI code, performs cache maintenance depending on entry state, initializes EL1/EL2 state, runs `__cpu_setup()`, enables the MMU, calls `__pi_early_map_kernel()` to map/relocate, then branches to `start_kernel()`. Secondary CPUs initialize EL state, verify VA support when needed, enable the MMU with idmap/swapper tables, set boot mode, install vectors, initialize task context, and enter `secondary_start_kernel()`.

Dependencies and integration: tightly coupled to linker symbols, page table layout, `arch/arm64/mm/proc.S`, hypervisor stub vectors, KASAN early init, KASLR PI mapping code, CPU boot mode flags, SMP holding pen, shadow call stack, pointer authentication, and EFI header generation.

Risks and test signals: risks include wrong endian/MMU state handling, insufficient cache maintenance before MMU-off execution, unsupported granule detection, EL2/VHE misconfiguration, broken early FDT preservation, and secondary CPU parking. Test signals are early boot across EL1/EL2/VHE/nVHE, big-endian builds, KASLR/relocatable kernels, 52-bit VA/LPA2 hardware, SMP bring-up, and bootloader Image header validation.
