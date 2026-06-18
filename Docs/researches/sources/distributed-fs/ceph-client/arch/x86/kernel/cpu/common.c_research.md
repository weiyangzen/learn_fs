# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/common.c

## Purpose
`common.c` is the main x86 CPU bring-up and feature-normalization pipeline. It owns early and full CPU identification, vendor driver dispatch, CPUID feature collection, bug-bit enumeration, command-line feature overrides, control-register setup/pinning, per-CPU GDT/TSS/syscall/debug state, boot and secondary CPU finalization, late microcode feature checks, SMT update hooks, and the final handoff to mitigation and alternatives setup.

## Important APIs, Types, and Functions
Global/per-CPU state includes `cpu_info`, `USER_PTR_MAX`, `elf_hwcap2`, topology count exports, `gdt_page`, forced capability bitmaps `cpu_caps_cleared` and `cpu_caps_set`, `current_task`, `__preempt_count`, `cpu_current_top_of_stack`, `__x86_call_depth`, and `__stack_chk_guard`.

CPU detection APIs include `init_cpu_devs()`, `early_cpu_init()`, `cpu_detect()`, `get_cpu_vendor()`, `get_cpu_cap()`, `get_cpu_address_sizes()`, `identify_boot_cpu()`, `identify_secondary_cpu()`, and `arch_cpu_finalize_init()`. Feature/bug logic includes `filter_cpuid_features()`, `init_speculation_control()`, `cpu_set_bug_bits()`, `parse_set_clear_cpuid()`, `cpu_parse_early_param()`, `check_null_seg_clears_base()`, and `detect_nopl()`.

Low-level setup APIs include `native_write_cr0()`, `native_write_cr4()`, `cr4_update_irqsoff()`, `cr4_read_shadow()`, `cr4_init()`, `load_direct_gdt()`, `load_fixmap_gdt()`, `switch_gdt_and_percpu_base()`, `setup_pku()`, `setup_cet()`, `cet_disable()`, `syscall_init()`, `cpu_init_exception_handling()`, `cpu_init_replace_early_idt()`, and `cpu_init()`.

## Control Flow
`early_cpu_init()` registers vendor descriptors from the linker section and runs `early_identify_cpu(&boot_cpu_data)`. Early identification does minimum CPUID/vendor/capability discovery, parses early feature-suppression options (`noxsave`, `clearcpuid`, `setcpuid`, `fred=off`, etc.), initializes topology, runs vendor early/BSP hooks, checks feature dependencies, sets bug bits, runs split-lock setup, clears impossible 32-bit capabilities, handles 5-level paging visibility, detects NOPL, and initializes MCE BSP state.

`arch_cpu_finalize_init()` later calls `identify_boot_cpu()`, sets SMT thread counts, selects the idle routine, runs `cpu_select_mitigations()` from `bugs.c`, updates SMT-sensitive subsystems, initializes FPU/EFI, copies final boot CPU data into the per-CPU slot, marks it initialized, and patches alternatives.

`identify_cpu()` is the full identification path used for boot and secondary CPUs. It resets fields, runs generic CPUID identification, parses topology, calls vendor identify/init hooks, runs bus-lock setup, configures SMEP/SMAP/UMIP, filters CPUID-level-dependent features, checks dependency consistency, chooses/fills model name, initializes random/PKEY/CET support, reapplies forced caps, intersects AP features into boot common caps, mirrors bug bits to APs, initializes PPIN/MCE/NUMA, and leaves a normalized `cpuinfo_x86`.

Secondary CPU bring-up uses `identify_secondary_cpu()`, then replays SEP where needed, SPEC_CTRL/AP mitigation MSRs, SRBDS/GDS MSRs, TSX AP setup, and marks the CPU initialized. Per-CPU runtime state is finalized through `cpu_init_exception_handling()` and `cpu_init()`.

## State and Persistence
Capability state is accumulated in `struct cpuinfo_x86` and global forced-cap bitmaps. Bug bits are synthesized from whitelist/blacklist tables, architectural capability MSR bits, hypervisor state, microcode revision, and vendor features. CR4 pinning records sensitive CR4 bits after CPU init and uses static-key guarded write wrappers to restore missing bits if later writes try to clear them. GDT/TSS/syscall/debug-register setup is per CPU and must be reloaded on CPU init, resume, and hotplug. Late microcode checks snapshot capabilities and warn if features change after loading.

## Dependencies and Integration Points
This file is the integration center for vendor files (`centaur.c`, `cyrix.c`, Intel/AMD/Hygon/etc. files), cache detection, topology, split/bus lock handling, vulnerability mitigation (`bugs.c`), CPUID dependency clearing (`cpuid-deps.c`), microcode, MCE, NUMA, APIC, FPU, EFI, FRED, TDX, SEV, PKU, CET/IBT, syscall/entry code, KVM exports for CR4/GDT, and CPU hotplug/SMT callbacks.

## Risks
Ordering is critical. Feature bits must be stable before alternatives and FPU/EFI choices; bug bits must exist before mitigation selection; forced `clearcpuid`/`setcpuid` changes must be applied after each CPUID probe; CR pinning must not start until the intended CR4 bits are known. Vendor hooks can mutate capabilities, so generic filters and dependency checks must run after them. Whitelist/blacklist bug tables are security-sensitive and require accurate CPU model/microcode data. Late microcode changes cannot fully re-patch all static alternatives, so the file warns instead of silently assuming changes take effect.

## Test Signals
Boot smoke tests should check dmesg CPU identification, model strings, feature flags in `/proc/cpuinfo`, topology debugfs, vulnerability sysfs, CR4 pinning warnings under LKDTM-style tests, `clearcpuid=`/`setcpuid=` taint and feature effects, AP hotplug, suspend/resume, late microcode warning paths, 32-bit SEP/syscall behavior where applicable, and virtualization paths for TDX/SEV/Xen/KVM.
