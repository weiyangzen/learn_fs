# subset-b-000885 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_common.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_common.c

## Purpose
Builds the common x86 CPU topology model from CPUID/APIC data and initializes global topology metadata used by scheduler, CPU hotplug, cache, and package/die/core ID code.

## Important APIs, Types, And Functions
Exports `x86_topo_system` and `__amd_nodes_per_pkg`. `topology_set_dom()` updates one topology domain and propagates defaults upward. `get_topology_cpu_type()` and `get_topology_cpu_type_name()` classify Intel/AMD hybrid CPUs. `cpu_parse_topology()` validates per-CPU topology after APIC setup, and `cpu_init_topology()` seeds boot-time global domain shifts and sizes.

## Control Flow
`parse_topology()` starts with safe defaults, handles CPUID-less/Xen PV fake topology, reads CPUID leaf 1 initial APIC ID, then dispatches to AMD/Hygon, Intel extended topology, or legacy core parsing. The boot CPU path stores global domain shifts in `x86_topo_system`; later CPUs recompute and warn if domain shifts or APIC IDs disagree.

## State, Persistence, And Dependencies
State is boot-lifetime kernel state: `cpuinfo_x86.topo`, global topology shifts/sizes, APIC-to-logical IDs, AMD node counts, and exported masks. It depends on CPUID helpers, APIC access, SMP topology registration, and vendor-specific parsers in sibling CPU code.

## Integration Points
Feeds scheduler topology, CPU masks, sysfs topology, cache IDs, AMD node handling, and firmware bug diagnostics. Intel extended parsing is delegated to `cpu_parse_topology_ext()`, while AMD fixups are delegated to AMD topology helpers.

## Risks
Malformed firmware/APIC/CPUID data can cause wrong package/core/die IDs. Legacy parsing depends on core counts and HT bits matching CPUID leaf 1. Early mode uses initial APIC ID because APIC mapping is not yet ready.

## Test Signals
Boot logs should not show APIC mismatch or topology-domain shift firmware bugs. CPU hotplug should produce stable logical package/die/core IDs across all CPUs. Hybrid Intel/AMD systems should report expected CPU type names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_ext.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_ext.c

## Purpose
Parses modern CPUID topology leaves and maps hardware level types into Linux x86 topology domains.

## Important APIs, Types, And Functions
`enum topo_types` mirrors CPUID topology type encodings. `topo_domain_map_0b_1f` maps Intel leaves `0xb`/`0x1f`; `topo_domain_map_80000026` maps AMD leaf `0x80000026`. `topo_subleaf()` decodes one subleaf and updates a `topo_scan`. `parse_topology_leaf()` walks subleafs. `cpu_parse_topology_ext()` chooses the best supported leaf.

## Control Flow
Intel tries leaf `0x1f`, AMD tries `0x80000026`, and both can fall back to `0x0b`. Each subleaf must have a processor count and nonzero type. Known types map to SMT/core/module/tile/die/die-group domains; unknown future types are placed after the previous domain with an error. The parser records x2APIC ID consistency and fixes broken SMT subleaf shift zero cases.

## State, Persistence, And Dependencies
It only mutates the caller-provided `topo_scan` and `cpuinfo_x86.topo.initial_apicid`, then sets `X86_FEATURE_XTOPOLOGY`. It depends on CPUID subleaf layout and common topology helpers.

## Integration Points
Called from Intel and AMD topology discovery in `topology_common.c`; its domain shifts are later copied into `x86_topo_system` or validated per CPU.

## Risks
Future or vendor-specific topology types may be guessed incorrectly. Broken firmware can advertise inconsistent APIC IDs or impossible SMT shifts. Domain map changes can affect scheduler grouping and package/core IDs.

## Test Signals
Boot on Intel leaf `0x1f`, Intel leaf `0x0b`, and AMD `0x80000026` systems should set `XTOPOLOGY` and produce stable topology domains without warnings except on known broken firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/transmeta.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/transmeta.c

## Purpose
Registers Transmeta CPUs and applies Transmeta-specific CPUID/MSR initialization, cache detection, revision reporting, and capability unmasking.

## Important APIs, Types, And Functions
`early_init_transmeta()` reads Transmeta CPUID leaf `0x80860001` capabilities. `init_transmeta()` reports CPU/CMS revisions, product string, cache sizes, unmasks hidden CPUID bits through MSR `0x80860004`, sets `CONSTANT_TSC`, and disables VA randomization under `CONFIG_SYSCTL`. `transmeta_cpu_dev` registers vendor strings.

## Control Flow
Early init caches extended Transmeta flags if available. Full init calls early init, detects cache sizes, prints revision leaves, assembles a 64-byte CPU information string from leaves `0x80860003` to `0x80860006`, temporarily unmasks CPUID capabilities via MSR, then restores the mask.

## State, Persistence, And Dependencies
State changes are CPU capability bits, `cpuinfo_x86.x86_capability`, printk diagnostics, and optionally global `randomize_va_space`. It depends on Transmeta CPUID leaves, MSRs, scheduler clock headers, and generic CPU vendor registration.

## Integration Points
Participates in x86 CPU vendor selection through `cpu_dev_register()`. Capabilities it exposes influence later feature setup and userspace CPUID visibility.

## Risks
MSR writes assume Transmeta behavior and must not run on misidentified CPUs. Disabling ASLR is a broad policy side effect. Product/revision leaves are legacy and may be absent or partially populated.

## Test Signals
Transmeta boot should print expected revisions, preserve restored capability-mask MSR, expose hidden standard CPUID capabilities correctly, and mark TSC constant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/transmeta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/tsx.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/tsx.c

## Purpose
Controls Intel TSX enumeration and runtime enablement/disablement based on config defaults, `tsx=` command line, microcode capabilities, and transient-execution mitigation state.

## Important APIs, Types, And Functions
`enum tsx_ctrl_states` tracks auto/on/off/always-abort/unsupported. `tsx_parse_cmdline()` handles `tsx=on|off|auto`. `tsx_init()` performs boot CPU policy. `tsx_ap_init()` applies the selected policy on APs. Helpers write `MSR_IA32_TSX_CTRL`, `MSR_TSX_FORCE_ABORT`, and `MSR_IA32_MCU_OPT_CTRL`.

## Control Flow
Boot first disables TSX development mode where TAA-sensitive microcode exposes `RTM_ALLOW`. If `RTM_ALWAYS_ABORT` is visible, TSX CPUID is cleared and RTM/HLE caps are cleared. Otherwise, the code requires `ARCH_CAP_TSX_CTRL_MSR`; unsupported hardware ignores policy. Auto disables TSX on TAA-affected systems and enables it otherwise. AP initialization repeats the selected MSR operation without changing global CPUID feature bits.

## State, Persistence, And Dependencies
`tsx_ctrl_state` is `__ro_after_init` after command-line parsing and init. CPU capability bits for RTM/HLE/MSR_TSX_CTRL and MSR values persist for the running kernel. It depends on architecture capabilities, vulnerability detection, and Intel microcode behavior.

## Integration Points
Feeds mitigation policy and userspace CPUID enumeration. AP paths integrate with CPU bring-up. The feature bits influence libraries and applications deciding whether to use RTM/HLE.

## Risks
Late microcode can change `RTM_ALWAYS_ABORT`; the code avoids late CPUID feature churn but still must clear hardware enumeration on APs. Enabling TSX can weaken TAA mitigation expectations. Incorrect MSR capability detection risks #GP.

## Test Signals
Boot with `tsx=on`, `tsx=off`, and `tsx=auto` should produce expected RTM/HLE CPUID visibility. TAA-affected hardware should default off in auto mode. CPU hotplug should preserve the selected TSX policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/tsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umc.c

## Purpose
Registers UMC 386/486-era CPUs with vendor identification and legacy model names.

## Important APIs, Types, And Functions
`umc_cpu_dev` declares vendor string `UMC`, CPUID identifier `UMC UMC UMC`, family 4 model names `U5D` and `U5S`, and vendor enum `X86_VENDOR_UMC`. `cpu_dev_register()` exposes it to generic CPU identification.

## Control Flow
There is no active init hook. Generic CPU detection matches the vendor string and uses the legacy model table for names.

## State, Persistence, And Dependencies
State is limited to static registration data. It depends on x86 CPU vendor infrastructure and legacy model-name lookup.

## Integration Points
Participates in CPU identification paths that populate `/proc/cpuinfo` and `cpuinfo_x86` vendor/model metadata.

## Risks
The file intentionally performs no quirks; if a UMC-compatible CPU needs feature masking or timing fixes, this registration will not supply them.

## Test Signals
Booting a matching UMC CPU or emulator should identify vendor/model without running any special init and without feature side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umwait.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umwait.c

## Purpose
Provides systemwide control for Intel WAITPKG `UMWAIT` behavior through `IA32_UMWAIT_CONTROL`, CPU hotplug callbacks, suspend/resume restoration, and sysfs knobs.

## Important APIs, Types, And Functions
`umwait_control_cached` stores the desired control value; `orig_umwait_control_cached` preserves BIOS/hardware state. `umwait_update_control_msr()` writes the MSR. `umwait_cpu_online()` and `umwait_cpu_offline()` program or restore CPUs. Sysfs attributes `enable_c02` and `max_time` live under `cpu/umwait_control`.

## Control Flow
`umwait_init()` exits unless `WAITPKG` is present, saves the original MSR, registers CPU hotplug state, registers syscore resume, and creates the sysfs group. Sysfs writes parse and validate input, take `umwait_lock`, update the cached control value, then call `on_each_cpu()` to propagate the MSR. Resume writes the cached value on the boot CPU; APs are handled by hotplug.

## State, Persistence, And Dependencies
State persists in cached globals and per-CPU MSR contents. Offline CPUs are restored to original MSR values. It depends on CPU hotplug, syscore suspend, CPU bus sysfs, MSR definitions, and WAITPKG capability.

## Integration Points
Exposes runtime power/latency policy to userspace and cooperates with CPU online/offline and system resume.

## Risks
Concurrent sysfs writes and CPU bring-up are race-prone; interrupts are disabled in online callback to order cached reads against IPIs. Invalid `max_time` bits return `-EINVAL`. Sysfs creation failure still leaves MSR defaults programmed.

## Test Signals
`/sys/devices/system/cpu/umwait_control/enable_c02` and `max_time` should reflect writes, reject invalid masks, and survive CPU hotplug and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umwait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vmware.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vmware.c

## Purpose
Detects VMware guests, selects hypercall transport, configures paravirtual time and steal-time accounting, and supplies encrypted-guest hypercall glue.

## Important APIs, Types, And Functions
`vmware_hypercall_slow()` implements I/O-port, `vmcall`, or `vmmcall` hypercalls. `vmware_platform()` detects CPUID/DMI VMware presence. `vmware_platform_setup()` reads TSC/bus frequencies, sets calibration hooks, and installs paravirt ops. `vmware_paravirt_ops_setup()` configures sched clock and steal clock. Optional exports include `vmware_tdx_hypercall()` and SEV-ES GHCB prepare/finish callbacks. `x86_hyper_vmware` registers the hypervisor.

## Control Flow
Detection prefers CPUID hypervisor vendor `VMwareVMware`, selecting hypercall mode from feature leaf `0x40000010`; legacy DMI falls back to port probing. Setup asks the hypervisor for frequency, overrides TSC and LAPIC calibration, handles SNP non-EFI MP table parsing, enables paravirt clock/steal-time if supported, disables IO-APIC timer checks, and forces TSC reliability caps. CPU hotplug registers per-CPU steal-time pages, and reboot disables them.

## State, Persistence, And Dependencies
Persistent state includes `vmware_tsc_khz`, `vmware_hypercall_mode`, per-CPU decrypted steal-time pages, paravirt static keys, clock conversion data, and modified x86 platform hooks. It depends on hypervisor CPUID leaves, VMware command ABI, APIC/timer code, paravirt, TDX, SEV-ES, and encrypted-memory attributes.

## Integration Points
Integrated through `hypervisor_x86`, `x86_platform` calibration hooks, `pv_info`, `pv_steal_clock`, `smp_ops`, CPU hotplug, reboot notifiers, and confidential-computing runtime hypercall callbacks.

## Risks
Incorrect detection can execute unsafe hypercalls. Steal-time registration depends on stable decrypted physical addresses. TDX and SEV-ES paths must preserve register ABI exactly. Forcing TSC reliable bypasses watchdog checks by trusting the hypervisor.

## Test Signals
VMware guests should report hypercall mode and TSC frequency, skip timer instability warnings, expose steal-time when available, handle CPU hotplug/reboot cleanly, and pass TDX/SEV-ES hypercall ABI tests where configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vortex.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vortex.c

## Purpose
Registers Vortex86 CPU vendor/model metadata without applying special initialization.

## Important APIs, Types, And Functions
`vortex_cpu_dev` declares vendor `Vortex`, CPUID identifier `Vortex86 SoC`, family/model names for Vortex86DX, MX, and EX, and vendor enum `X86_VENDOR_VORTEX`.

## Control Flow
CPU identification matches the vendor string and uses legacy model tables. The family 6 model 0 name is only a fallback for Vortex86EX; EX2 can provide a product-name CPUID string elsewhere.

## State, Persistence, And Dependencies
Only static CPU vendor registration state is introduced. It depends on generic CPU detection and legacy model name formatting.

## Integration Points
Feeds vendor/model display and `cpuinfo_x86` vendor selection for Vortex86 systems.

## Risks
No quirks are applied. Any future Vortex CPU requiring feature masking, timer handling, or cache setup must be added elsewhere.

## Test Signals
Matching systems should identify as Vortex and print the expected model name without additional init side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vortex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/zhaoxin.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/zhaoxin.c

## Purpose
Registers Zhaoxin CPUs and applies vendor-specific capability setup for TSC behavior, cache/perf features, crypto/RNG units, and IA32 feature control.

## Important APIs, Types, And Functions
`early_init_zhaoxin()` sets constant/nonstop TSC capabilities. `init_zhaoxin_cap()` enables ACE crypto and RNG units via `MSR_ZHAOXIN_FCR57` when CPUID reports present-but-disabled units, stores extended capability flags, and sets `REP_GOOD`. `init_zhaoxin()` initializes cache info, architectural perfmon, LFENCE/RDTSC on 64-bit, and feature control.

## Control Flow
Early init handles TSC caps. Full init repeats early init, initializes Intel-like cache info, checks CPUID leaf 10 for usable perf counters, then enables Zhaoxin extended units and feature caps for family 6+. Vendor registration matches CPUID identifier `"  Shanghai  "`.

## State, Persistence, And Dependencies
State is CPU capability bits, CPUID capability arrays, and MSR-enabled ACE/RNG units. It depends on CPUID extended leaf `0xC0000001`, Zhaoxin MSR `0x1257`, Intel-style cache/perf helpers, and feature-control initialization.

## Integration Points
Participates in x86 CPU vendor init and affects crypto/RNG feature visibility, perf events, TSC clocksource trust, and virtualization feature control.

## Risks
MSR bit definitions are vendor-specific. Enabling units based on CPUID must match hardware behavior. Treating Zhaoxin like Intel for cache/perf helpers can miss vendor deviations.

## Test Signals
Boot should enable ACE/RNG only when present and disabled, set constant/nonstop TSC where advertised, expose arch perfmon when leaf 10 is valid, and avoid MSR faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/zhaoxin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpuid.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpuid.c

## Purpose
Implements the `/dev/cpu/<n>/cpuid` character device, allowing userspace to read CPUID leaves on a selected online CPU.

## Important APIs, Types, And Functions
`struct cpuid_regs_done` bundles CPUID registers and a completion. `cpuid_read()` validates 16-byte reads and issues CPUID operations on the target CPU. `cpuid_open()` validates CPU existence, online state, and CPUID support. `cpuid_init()` registers major `CPUID_MAJOR`, class `cpuid`, and CPU hotplug device creation.

## Control Flow
Userspace seeks to a 64-bit position where low 32 bits become EAX and high 32 bits become ECX. Reads must be multiples of 16 bytes; each chunk schedules `cpuid_smp_cpuid()` on the minor-number CPU with `smp_call_function_single_async()`, waits for completion, copies four registers to userspace, increments the position, and repeats.

## State, Persistence, And Dependencies
Persistent state is the registered char device, device class, and dynamic CPU hotplug state ID. It depends on CPU hotplug, SMP calls, completions, uaccess, and CPUID helpers.

## Integration Points
Creates `/dev/cpu/%u/cpuid` nodes and integrates with CPU online/offline to add/remove devices.

## Risks
The target CPU can go offline after open or during read, returning errors from SMP calls. Count alignment is strict. Userspace-visible CPUID reflects kernel feature masking and CPU-specific CPUID state.

## Test Signals
Module load should create devices for online CPUs. Reads of 16-byte chunks should match native CPUID on the target CPU; odd sizes should return `-EINVAL`; offline or unsupported CPUs should fail open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/crash.c

## Purpose
Provides x86 crash-kexec shutdown, crash dump ELF header construction, crash-kernel memory map setup, segment loading, and crash hotplug ELF core header updates.

## Important APIs, Types, And Functions
`native_machine_crash_shutdown()` performs minimal machine shutdown for crash kexec. `crash_smp_send_stop()` and `kdump_nmi_shootdown_cpus()` stop other CPUs. `prepare_elf_headers()` builds RAM PT_LOAD headers excluding crash regions. `crash_setup_memmap_entries()` builds E820 entries for the dump kernel. `crash_load_segments()` loads ELF headers. `arch_crash_handle_hotplug_event()` updates elfcorehdr in place.

## Control Flow
Crash shutdown disables interrupts, stops other CPUs, disables virtualization and Intel PT, clears IO-APIC/LAPIC/HPET state, runs encrypted-guest kexec hooks, and saves CPU regs. File-based crash loading gathers RAM resources, excludes low 1M, crashkernel, low crashkernel, CMA, elf headers, and dm-crypt key ranges, then places ELF headers as a kexec segment. Hotplug rebuilds headers and copies them into the existing segment under temporary `kexec_crash_image` invalidation.

## State, Persistence, And Dependencies
State includes crash resources, kexec image fields, generated ELF headers, boot params E820 entries, and saved CPU notes. It depends on kexec, memblock/resource walking, APIC/IO-APIC/HPET, Intel PT, SEV/guest encryption hooks, and crash memory helpers.

## Integration Points
Hooks into panic/crash_kexec, kexec_file_load, crash hotplug, encrypted guest transitions, and dump-kernel boot parameter construction.

## Risks
Crash context is fragile: locks may be held, CPUs may be wedged, and only minimal operations are safe. Header sizing must account for maximum CPUs/memory ranges. Exclusion mistakes can cause dump kernel overwrite or missing memory.

## Test Signals
Crash dumps should boot reliably, include correct RAM ranges, exclude crashkernel/key/header regions, update elfcorehdr on CPU/memory hotplug, and avoid IO-APIC/APIC deadlocks during panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_32.c

## Purpose
Implements 32-bit kdump old-memory page copying with PAE safety checks.

## Important APIs, Types, And Functions
`is_crashed_pfn_valid()` rejects PFNs that cannot round-trip through a PTE on non-PAE kernels. `copy_oldmem_page()` maps a crashed-kernel PFN with `kmap_local_pfn()`, copies data to an `iov_iter`, and unmaps it.

## Control Flow
Zero-length copies return immediately. Non-PAE kernels validate the PFN to avoid address truncation when a non-PAE dump kernel reads memory from a PAE crashed kernel. Valid pages are locally mapped, copied from `offset` for `csize`, then unmapped.

## State, Persistence, And Dependencies
No persistent state is introduced. It depends on highmem local PFN mappings, `iov_iter`, PTE encoding, and crash dump read paths.

## Integration Points
Used by `/proc/vmcore` and crash dump infrastructure to read physical memory from the previous kernel on 32-bit x86.

## Risks
Invalid PFNs must be rejected to avoid aliasing high physical memory into low addresses. The caller must supply sane offsets and sizes within a page.

## Test Signals
32-bit kdump reads should return exact page data; non-PAE dump kernels should reject unrepresentable PFNs with `-EFAULT`; zero-size reads should return 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_64.c

## Purpose
Implements 64-bit kdump old-memory and elfcorehdr reads, including encrypted-memory mappings for SME/confidential guests.

## Important APIs, Types, And Functions
`__copy_oldmem_page()` maps a physical page with either `ioremap_cache()` or `ioremap_encrypted()`. `copy_oldmem_page()` reads normal old memory. `copy_oldmem_page_encrypted()` reads encrypted old memory. `elfcorehdr_read()` reads through `read_from_oldmem()` using guest memory encryption state.

## Control Flow
Zero-length copies return 0. The helper maps the PFN as a full page, copies from `offset` to the iterator, unmaps, and returns copied bytes or `-ENOMEM` on map failure. `elfcorehdr_read()` wraps a kernel buffer in a `kvec` iterator and chooses encrypted reads when `CC_ATTR_GUEST_MEM_ENCRYPT` is active.

## State, Persistence, And Dependencies
No persistent state is introduced. It depends on ioremap attributes, confidential-computing platform flags, `iov_iter`, and crash dump old-memory helpers.

## Integration Points
Supports `/proc/vmcore`, crash ELF header reading, and encrypted-memory dump capture on x86_64.

## Risks
Using the wrong encryption attribute produces unreadable or corrupt dumps. Mapping failures must propagate. Offsets and sizes are assumed page-bounded by callers.

## Test Signals
kdump should read vmcore pages and elfcorehdr correctly on normal, SME, and guest-encrypted systems, with encrypted and unencrypted paths producing expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/crash_dump_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/devicetree.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/devicetree.c

## Purpose
Adds x86 Open Firmware/devicetree boot support, especially for Intel CE4100-style APIC, HPET, PCI, CPU, and platform-device discovery.

## Important APIs, Types, And Functions
`add_dtb()` records setup-data DTB address. `x86_flattree_get_config()` maps, verifies, unflattens, and installs DT SMP parsing. `x86_of_pci_init()` replaces PCI IRQ hooks. `dtb_lapic_setup()`, `dtb_cpu_setup()`, and `dtb_ioapic_setup()` configure APICs. `dt_irqdomain_alloc()` converts DT IO-APIC firmware specifiers into mp irqdomain allocations.

## Control Flow
Early boot records DTB data pointer, maps enough bytes to read total FDT size, verifies and copies the tree, then, when ACPI is disabled and DT exists, replaces MP-table parsing with DT parsing. DT parsing configures HPET address, LAPIC address/mode, CPU APIC IDs and NUMA nodes, and IO-APIC domains. Later device init probes compatible CE4100 buses and PCI IRQ enable maps DT PCI interrupts.

## State, Persistence, And Dependencies
State includes `initial_dtb`, `cmd_line`, `of_ioapic`, registered APIC/IO-APIC state, HPET address, PCI IRQ hooks, and populated OF nodes. It depends on OF/FDT, APIC/IO-APIC, irqdomain, PCI, HPET, ACPI-disabled mode, and NUMA helpers.

## Integration Points
Bridges devicetree into x86 SMP discovery, PCI IRQ assignment, platform device creation, and interrupt domain allocation.

## Risks
Malformed DT interrupt parameters or missing APIC IDs break interrupt routing. Mapping only the initial DTB window requires correct `fdt_totalsize()`. This path is sensitive to ACPI-vs-DT boot mode.

## Test Signals
DT-booted x86 should populate devices, register LAPIC/IO-APIC, assign PCI IRQs through OF, and avoid MP-table parsing when ACPI is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/devicetree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/doublefault_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/doublefault_32.c

## Purpose
Sets up the 32-bit double-fault task gate/TSS stack and converts task-switch state into `pt_regs` for the common double-fault handler.

## Important APIs, Types, And Functions
`doublefault_shim()` is the non-returning C shim entered after the double-fault task switch. `doublefault_stack` is per-CPU page-aligned TSS/stack storage. `set_df_gdt_entry()` writes the GDT TSS descriptor. `doublefault_init_cpu_tss()` initializes per-CPU stack pointer and descriptor.

## Control Flow
The shim saves CR2, reloads the normal task register, reinstalls the double-fault GDT entry, marks hard IRQs off, builds a synthetic `pt_regs` from the double-fault TSS slots, calls `exc_double_fault()`, and panics because x86_32 cannot reconstruct CR3 safely after the task switch.

## State, Persistence, And Dependencies
Persistent per-CPU state is the double-fault TSS and stack in the CPU entry area. It depends on GDT/TSS helpers, CPU entry area layout, trap handling, and low-level assembly entry.

## Integration Points
Works with `asm_exc_double_fault`, common exception handling, and `dumpstack_32.c` stack recognition of double-fault stacks.

## Risks
This code runs in a catastrophic fault path and cannot return. Incorrect TSS descriptors or stack pointers can triple-fault. The synthetic regs are not visible to the unwinder as a normal frame.

## Test Signals
Forced double faults on 32-bit kernels should reach the double-fault oops path with meaningful registers and stack trace instead of immediate reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/doublefault_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack.c

## Purpose
Implements common x86 stack tracing, opcode/register display, and oops/die lifecycle handling.

## Important APIs, Types, And Functions
`in_task_stack()` and `in_entry_stack()` classify stacks. `show_opcodes()`, `show_ip()`, `show_iret_regs()`, `show_stack()`, `show_stack_regs()`, and `show_regs()` print diagnostic state. `oops_begin()`, `oops_end()`, `__die()`, `die()`, and `die_addr()` coordinate oops reporting, locking, tainting, crash-kexec, and task termination.

## Control Flow
Trace printing starts an unwind, then walks valid stack regions returned by arch-specific `get_stack_info()`, printing reliable unwinder return addresses and unreliable text-address hints. Oops handling enters verbose console mode under `die_lock`, prints headers/registers/modules, notifies die hooks, optionally crash-kexecs, taints the kernel, restores IRQ state, prints an executive summary, and either returns, panics, or rewinds the stack to kill the task.

## State, Persistence, And Dependencies
State includes `die_counter`, `exec_summary_regs`, `die_lock`, owner/nesting counters, kernel taint, and console spinlock state. It depends on unwinder, stacktrace helpers, ftrace graph return fixups, KASAN/KMSAN suppression, notifier chains, kexec, and trap regs.

## Integration Points
Used by exception, WARN/oops, sysrq stack dumps, crash paths, and architecture-specific stack classifiers in `dumpstack_32.c` and `dumpstack_64.c`.

## Risks
Stack walking may run from NMI/oops contexts and must avoid faults, sanitizer false positives, and recursion. Oops lock handling intentionally trades strictness for avoiding deadlock. User opcode copying is restricted to current.

## Test Signals
Fault injection should print code bytes, registers, stack sections, reliable markers, module list, oops count, and correct panic/crash behavior according to policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_32.c

## Purpose
Provides 32-bit x86 stack classification for task, entry, hardirq, softirq, and double-fault stacks.

## Important APIs, Types, And Functions
`stack_type_name()` names stack types. `in_hardirq_stack()`, `in_softirq_stack()`, and `in_doublefault_stack()` identify special stacks and set `next_sp`. `get_stack_info()` is the exported classifier used by common dumpstack/unwinder code.

## Control Flow
`get_stack_info()` checks task stack first, then only for current checks entry, hardirq, softirq, and double-fault stacks. Each match fills begin/end/type/next_sp. A visit mask detects stack recursion and reports unknown if a stack type repeats.

## State, Persistence, And Dependencies
No new persistent state is created; it reads per-CPU irq stack pointers, CPU entry area double-fault stack, and current TSS saved SP. It depends on 32-bit IRQ stack layout and double-fault TSS setup.

## Integration Points
Feeds `dumpstack.c` stack walking and frame transition logic on 32-bit kernels.

## Risks
Stack boundary checks differ for software stacks where `end` may be a valid empty-stack pointer. Incorrect `next_sp` extraction can truncate traces or recurse.

## Test Signals
32-bit traces from task, IRQ, softirq, entry, and double-fault contexts should label stacks correctly and stop on recursive or invalid stack transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_64.c

## Purpose
Provides 64-bit x86 stack classification for task, IRQ, entry trampoline, and IST exception stacks.

## Important APIs, Types, And Functions
`stack_type_name()` names task/IRQ/softirq/entry and exception stack types. `struct estack_pages` maps CPU entry area exception stack pages to stack metadata. `in_exception_stack()` and `in_irq_stack()` identify special stacks. `get_stack_info_noinstr()` is noinstr-safe; `get_stack_info()` adds recursion checks.

## Control Flow
The classifier checks the task stack first, then for current checks exception stacks, IRQ stack, and entry stack. Exception stack lookup computes an offset in `cea_exception_stacks`, rejects guard pages, and derives `next_sp` from the pt_regs at the stack top. IRQ stack lookup adjusts the stored top pointer and reads the saved next stack pointer from the top entry.

## State, Persistence, And Dependencies
State is static exception page descriptors; runtime reads CPU entry area and hardirq stack pointers. It depends on CEA layout, IST stack sizes, IRQ stack switching ABI, and stacktrace interfaces.

## Integration Points
Used by common dumpstack and unwinder code, including noinstr contexts where instrumentation must be avoided.

## Risks
CEA exception stacks may be uninitialized early, so the code must fail gracefully. Guard pages must remain unclassified. Wrong next-SP computation can hide entry frames or loop traces.

## Test Signals
64-bit fault/NMI/#DB/#MC/#VC/IRQ traces should label stacks accurately, include transitions back to interrupted stacks, and warn once on recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/dumpstack_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/e820.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/e820.c

## Purpose
Owns low-level x86 E820 memory map ingestion, sanitization, command-line modification, memblock setup, resource registration, kexec firmware map export, and hibernation/no-save metadata.

## Important APIs, Types, And Functions
Global maps are `e820_table`, `e820_table_kexec`, and `e820_table_firmware`. Query/update APIs include `e820__mapped_any()`, `e820__mapped_all()`, `e820__get_entry_type()`, `e820__range_add()`, `e820__range_update()`, and `e820__range_remove()`. `e820__update_table()` resolves overlaps. Setup APIs include `e820__memory_setup()`, `e820__memblock_setup()`, `e820__reserve_resources()`, and `e820__reserve_resources_late()`.

## Control Flow
Boot copies BIOS or fallback memory data, sanitizes overlaps using sorted change points and highest-type precedence, mirrors the result into kexec and firmware tables, then applies early `mem=`/`memmap=` edits. Extended setup-data E820 entries are appended and re-sanitized. Memblock setup adds RAM, reserves soft-reserved regions, trims partial pages, and handles hotplug bottom-up allocation. Resource setup publishes system RAM and special memory to `/proc/iomem`, firmware map, and late device-resource discovery.

## State, Persistence, And Dependencies
Early `__initdata` tables are later reallocated to right-sized persistent memory. `pci_mem_start`, `userdef`, resource arrays, firmware-map entries, nosave regions, ACPI NVS registration, memblock regions, and kexec table changes persist. Dependencies include boot params, setup_data, memblock, ACPI, resource tree, firmware-map, KVM exports, suspend, and command-line parsing.

## Integration Points
Feeds physical memory discovery, page allocator bootstrap, PCI MMIO gap selection, hibernation CRC/no-save/NVS handling, kexec/kdump E820 propagation, sysfs firmware memmap, soft-reserved memory drivers, and `/proc/iomem`.

## Risks
Overlap sanitization, type precedence, and non-mergeable PRAM/soft-reserved ranges are correctness-critical. Overflow handling must reject wrapped entries. User-supplied maps can remove too much memory or create invalid maps. Late resource gaps are heuristics for firmware omissions.

## Test Signals
Boot logs should show sane BIOS/user/modified maps, memblock ranges should match RAM E820 entries, `mem=` and `memmap=` should reshape maps as expected, kexec should receive firmware-compatible maps, and `/proc/iomem` should expose RAM/special ranges without resource conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/e820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/early-quirks.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/early-quirks.c

## Purpose
Applies very early PCI/chipset workarounds before the normal PCI subsystem and timers are available.

## Important APIs, Types, And Functions
`early_quirks()` starts bus scanning. `check_dev_quirk()` matches devices against `early_qrk`. Quirk handlers adjust HyperTransport APIC broadcast, VIA GART IOMMU policy, NVIDIA/ATI timer overrides, Intel IRQ remapping brokenness, Intel graphics stolen memory reservation, Baytrail HPET disablement, and Apple AirPort reset. `intel_graphics_stolen_res` exports reserved graphics memory.

## Control Flow
If early PCI config access is allowed, bus 0 is scanned slot/function by slot/function, recursing into PCI bridges. For each device, config space class/vendor/device are compared to quirk entries; apply-once entries set flags. Intel graphics matching uses a large device-ID table with per-generation stolen-memory base/size callbacks, then reserves the stolen range in E820.

## State, Persistence, And Dependencies
State changes include PCI config writes, ACPI timer override flags, IOMMU disable flags, IRQ remapping broken state, `boot_hpet_disable`, E820 reserved ranges, exported graphics stolen resource, and device reset side effects. It depends on direct PCI config access, E820, APIC/IO-APIC/HPET, GART, irq remapping, early ioremap, DRM Intel PCI IDs, and Apple platform detection.

## Integration Points
Runs before normal PCI quirks to protect timers, interrupts, IOMMU, graphics stolen memory, and problematic devices during early boot.

## Risks
Direct PCI probing can touch fragile devices, so matching and single-function handling matter. Stolen-memory calculations are generation-specific. Reserving wrong E820 ranges can hide usable RAM or expose stolen RAM to MMIO.

## Test Signals
Affected chipsets should log expected quirks, avoid timer override regressions, reserve Intel graphics stolen memory, disable unreliable HPET, mark broken IRQ remapping, and leave normal PCI enumeration intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/early-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/early_printk.c

## Purpose
Implements legacy `earlyprintk=` consoles for VGA, I/O serial, MMIO serial, PCI serial, Xen HVC, EHCI debug port, and xDBC before regular consoles initialize.

## Important APIs, Types, And Functions
`early_vga_write()` writes text mode VGA memory. `early_serial_putc()` and `early_serial_write()` write UART output through static-call selected I/O or MMIO functions. `early_serial_init()`, `early_mmio_serial_init()`, and `early_pci_serial_init()` parse console options. `early_console_register()` registers the selected boot console. `setup_early_printk()` is the early parameter handler.

## Control Flow
The parser scans the `earlyprintk=` string for known backends and optional `keep`. Serial setup chooses default or requested port/baud, initializes UART registers unless `nocfg`, and updates kexec debug port globals where applicable. PCI serial validates BDF/class unless `force`, enables I/O or memory decode, maps BAR0 if needed, then initializes hardware. VGA uses boot screen geometry and scrolls manually.

## State, Persistence, And Dependencies
State includes current VGA cursor, serial base address, static calls for serial accessors, registered `early_console`, and optional kexec debug port addresses. It depends on early I/O, early ioremap, PCI direct config access, console core, boot params, Xen HVC, and optional USB debug backends.

## Integration Points
Provides early boot diagnostics before full console drivers and can be retained with `keep`. Kexec debug paths reuse discovered serial ports.

## Risks
Incorrect MMIO/PCI addresses can fault or write device memory. Only 32-bit MMIO addresses are supported in `mmio32`. The parser scans substrings incrementally, so option syntax must remain compatible.

## Test Signals
Booting with `earlyprintk=vga`, `serial`, `ttyS`, `mmio32`, and `pciserial` should print early logs, honor baud/nocfg/keep, and avoid duplicate console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ebda.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ebda.c

## Purpose
Conservatively reserves low conventional BIOS/EBDA firmware memory so the kernel does not allocate RAM used by BIOS or legacy DMA devices.

## Important APIs, Types, And Functions
`reserve_bios_regions()` reads the BIOS RAM size word at `0x413`, consults `get_bios_ebda()`, clamps to sane bounds, and reserves from the detected BIOS start to 1 MiB with `memblock_reserve()`.

## Control Flow
The function exits for platforms that disable legacy BIOS reservation. Otherwise it converts the BIOS kilobyte count to bytes, distrusts values outside 128 KiB to 640 KiB, lowers the start if EBDA begins earlier in a sane range, and reserves everything up to the 1 MiB mark.

## State, Persistence, And Dependencies
State is a memblock reservation in the low megabyte. It depends on legacy platform policy, BIOS data area mapping, EBDA probing, and memblock.

## Integration Points
Runs during early memory setup and protects the real-mode trampoline area from overlapping with firmware-reserved conventional memory.

## Risks
The code intentionally over-reserves when firmware data is suspicious. Reserving too little risks corrupting BIOS/EBDA or DMA state; reserving too much can starve low-memory trampoline allocations on tiny systems.

## Test Signals
Boot logs/memblock dumps should show low-memory reservations; systems with bogus BIOS RAM size should still reserve from 640 KiB; paravirtual platforms should skip this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ebda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/eisa.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/eisa.c

## Purpose
Detects legacy EISA bus presence on x86 by checking the EISA signature in low physical memory.

## Important APIs, Types, And Functions
`eisa_bus_probe()` maps physical address `0x0FFFD9`, checks for the four-byte `"EISA"` signature, and sets global `EISA_bus`. It is registered with `subsys_initcall()`.

## Control Flow
The probe skips non-initial Xen PV domains and SEV-SNP guests. Otherwise it maps the signature location write-back, compares the little-endian signature, sets `EISA_bus` if matched, unmaps, and returns success.

## State, Persistence, And Dependencies
Persistent state is the global `EISA_bus` flag. It depends on `memremap()`, Xen domain checks, confidential-computing attributes, and EISA core state.

## Integration Points
Allows legacy EISA subsystem probing only when the platform signature exists and is safe to access.

## Risks
Reading legacy physical addresses can be invalid in virtual or confidential guests, so explicit skips matter. Mapping failure currently still calls `memunmap(p)` with a possibly null pointer expectation based on kernel API tolerance.

## Test Signals
Real or emulated EISA machines should set `EISA_bus=1`; Xen PV non-dom0 and SNP guests should skip probing without faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/eisa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/espfix_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/espfix_64.c

## Purpose
Builds the 64-bit ESPFIX alias-stack mapping that prevents 16-bit IRET from truncating RSP and leaking kernel stack bits.

## Important APIs, Types, And Functions
Per-CPU `espfix_stack` and `espfix_waddr` expose alias and writable addresses. `init_espfix_bsp()` installs the PUD and randomization on the boot CPU. `init_espfix_ap()` allocates per-page ministacks and page tables for CPUs. `espfix_base_addr()` computes randomized alias addresses.

## Control Flow
FRED-capable systems skip ESPFIX because FRED restores full RSP. BSP init attaches `espfix_pud_page` under `ESPFIX_BASE_ADDR`, randomizes page/slot selection, then initializes CPU 0. AP init returns if already done, computes the alias, shares one physical page across several CPU ministacks, lazily allocates missing PUD/PMD/PTE levels under a mutex, maps clones 64 KiB apart read-only/global/encrypted, then records readable alias and writable kernel address.

## State, Persistence, And Dependencies
State includes per-CPU stack addresses, `espfix_pages[]`, shared page-table pages, randomization seeds, and kernel page-table entries. It depends on paging constants, CPU node allocation, paravirt page-table allocation hooks, encryption page bits, and entry assembly using the ministack.

## Integration Points
Entry code uses these aliases when returning to 16-bit LDT stack segments. Double-fault handling repairs faults caused by read-only ministacks.

## Risks
Alias math and clone counts must match page-table geometry. Allocation races are protected by a mutex, but page-table initialization must be globally visible. Misconfiguration can break 16-bit compatibility or leak stack addresses.

## Test Signals
16-bit/LDT IRET tests on non-FRED x86_64 should not truncate or leak RSP; CPU hotplug should initialize per-CPU ESPFIX addresses once; FRED systems should skip setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/espfix_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/Makefile

## Purpose
Defines the built-in object list for x86 kernel FPU support.

## Important APIs, Types, And Functions
The `obj-y` rule builds `init.o`, `bugs.o`, `core.o`, `regset.o`, `signal.o`, and `xstate.o` into the kernel FPU subsystem.

## Control Flow
There is no runtime control flow. Kbuild compiles and links the listed objects whenever this directory is included in the architecture build.

## State, Persistence, And Dependencies
The file contributes build-time state only. Runtime dependencies are expressed by the object files it includes; notably `xstate.o` is required even though it is outside this work item.

## Integration Points
Connects FPU initialization, bug checks, core context management, ptrace/core-dump regsets, signal frames, and xstate handling into the architecture kernel.

## Risks
Removing or reordering objects can cause missing symbols or initialization dependencies. Adding FPU files requires updating this list or related conditional Kbuild rules.

## Test Signals
Architecture builds should link all FPU symbols, and boot should execute FPU initialization without unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/bugs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/bugs.c

## Purpose
Performs boot-time detection of the classic Pentium FDIV FPU bug.

## Important APIs, Types, And Functions
`fpu__init_check_bugs()` uses `kernel_fpu_begin()`/`kernel_fpu_end()` and inline x87 instructions over constants `4195835.0` and `3145727.0`; it sets `X86_BUG_FDIV` on `boot_cpu_data` when the computed result is nonzero.

## Control Flow
If the boot CPU lacks hardware FPU, the check exits. Otherwise it enters a kernel FPU section, initializes x87 state, performs divide/multiply/subtract, stores the integer residual, exits the FPU section, and warns if a bug is detected.

## State, Persistence, And Dependencies
Persistent state is the CPU bug bit and warning. It depends on patched alternatives being ready for kernel FPU usage, hardware FPU availability, and x87 instruction behavior.

## Integration Points
Runs during CPU/FPU bug checks and influences `/proc/cpuinfo` bug reporting and mitigation awareness.

## Risks
Must not run before kernel FPU use is legal. The test intentionally ignores non-bug feature/status reporting.

## Test Signals
Normal CPUs should leave `X86_BUG_FDIV` clear. Emulated buggy FDIV behavior should set the bug bit and log the warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/bugs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/context.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/context.h

## Purpose
Defines inline helpers for tracking whether a task's FPU register state is currently valid in CPU registers.

## Important APIs, Types, And Functions
`__cpu_invalidate_fpregs_state()` clears the per-CPU owner. `__fpu_invalidate_fpregs_state()` invalidates a task by setting `last_cpu=-1`. `fpregs_state_valid()` checks owner and CPU. `fpregs_activate()`/`fpregs_deactivate()` update ownership and trace. `fpregs_restore_userregs()` restores current user registers when needed.

## Control Flow
Lazy restore paths check whether current's `struct fpu` owns the CPU registers. If not, `restore_fpregs_from_fpstate()` loads all user FPU state except parts handled eagerly or specially, marks the FPU active, records `last_cpu`, and clears `TIF_NEED_FPU_LOAD`.

## State, Persistence, And Dependencies
State is `fpu_fpregs_owner_ctx`, `fpu->last_cpu`, and current thread flags. It depends on xstate restore helpers, PKRU/XFD rules, scheduler current task state, and FPU tracepoints.

## Integration Points
Included by FPU core, signal, and regset paths to coordinate lazy FPU state with context switches, ptrace, signal return, and kernel FPU sections.

## Risks
Any code that modifies FPU registers or task fpstate must invalidate ownership correctly; otherwise stale registers can overwrite modified memory state or leak between tasks.

## Test Signals
Context switch, ptrace modification, signal restore, and kernel FPU use should force reloads only when needed and never run user tasks with stale register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/core.c

## Purpose
Implements central x86 FPU state management: register save/restore, lazy ownership tracking, kernel FPU sections, task clone/reset/drop, exception decoding, KVM guest fpstate swapping, dynamic XFD handling, and idle cleanup.

## Important APIs, Types, And Functions
Global configs are `fpu_kernel_cfg`, `fpu_user_cfg`, `guest_default_cfg`, and `init_fpstate`. Per-CPU state includes `kernel_fpu_allowed`, `fpu_fpregs_owner_ctx`, and x86_64 `xfd_state`. Key APIs include `save_fpregs_to_fpstate()`, `restore_fpregs_from_fpstate()`, `kernel_fpu_begin_mask()`, `kernel_fpu_end()`, `fpu_clone()`, `fpu__clear_user_states()`, `switch_fpu_return()`, `fpregs_mark_activate()`, and KVM exports such as `fpu_swap_kvm_fpstate()`.

## Control Flow
Save/restore chooses XSAVE, FXSAVE, or legacy FSAVE/FRSTOR based on CPU features. Kernel FPU begin locks fpregs, marks kernel FPU unavailable, saves current user state if loaded, invalidates ownership, and initializes MXCSR/x87 as requested; end re-enables use and unlocks. Fork resets destination FPU, optionally copies parent state, inherits permissions, clears caller-saved dynamic state, and updates shadow-stack state. KVM swaps current task fpstate with guest fpstate around VM entry/exit and keeps XFD synchronized.

## State, Persistence, And Dependencies
State spans task-embedded `struct fpu`, fpstate buffers, permission masks, XFD MSR state, AVX512 timestamps, PKRU, thread flags, and per-CPU ownership. It depends on xstate helpers, KVM, pkeys, CET shadow stack, IRQ/preemption locking, tracepoints, and CPU feature flags.

## Integration Points
Used by scheduler context switching, signal frames, ptrace/core dumps, KVM, kernel crypto/math users, fork/exec, exception handling, and cpuidle AMX cleanup.

## Risks
FPU state corruption is high impact. Risks include incorrect lazy restore invalidation, using FPU in NMI or nested hardirq contexts, mishandling supervisor xstates, XFD state mismatch causing #NM, and KVM guest/host ABI divergence.

## Test Signals
Stress context switches, signal delivery/return, ptrace writes, KVM save/restore, AMX/XFD allocation, kernel_fpu_begin nesting checks, AVX512 use tracking, and fork/exec should show no FPU leaks or invalid exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/init.c

## Purpose
Performs boot and CPU-online FPU initialization, legacy no-CPUID probing, MXCSR mask detection, xstate sizing bootstrap, and dynamic task-struct sizing.

## Important APIs, Types, And Functions
`fpu__init_cpu()` initializes CR0/CR4 and CPU xstate, then enables kernel FPU use on the CPU. `fpu__probe_without_cpuid()` detects legacy FPU presence. `fpu__init_system()` is the boot CPU orchestration entry. Helpers initialize MXCSR mask, default fpstate, legacy xstate sizes, and `arch_task_struct_size`.

## Control Flow
System init sets `TIF_NEED_FPU_LOAD`, probes FPU if CPUID is unavailable, halts if no FPU and no math emulation, initializes the boot CPU FPU, builds default fpstate, reads MXCSR mask through FXSAVE, seeds legacy sizes, calls xstate initialization, and computes the task allocation size with the dynamic fpstate size. CPU-online init sets CR4 OSFXSR/OSXMMEXCPT, clears CR0 TS/EM as appropriate, initializes x87, and enables kernel FPU sections.

## State, Persistence, And Dependencies
Persistent state includes CPU feature caps, `mxcsr_feature_mask`, `init_fpstate`, FPU config sizes/features, `arch_task_struct_size`, CR0/CR4 bits, and per-CPU `kernel_fpu_allowed`. It depends on xstate init, task allocation layout, math emulation config, and CPU feature detection.

## Integration Points
Runs before task creation and CPU hotplug FPU usage; its sizing directly affects task slab layout and `x86_task_fpu()` pointer arithmetic.

## Risks
Task-struct sizing requires `struct fpu.__fpstate` to remain last. Incorrect MXCSR mask or xstate sizes break signal/ptrace/KVM ABIs. FPU absence without emulation is fatal by design.

## Test Signals
Boot should report valid FPU/xstate sizing, online CPUs should allow kernel FPU after init, no-CPUID legacy systems should probe accurately, and task allocation should satisfy FPU alignment assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/internal.h

## Purpose
Provides small internal helpers and declarations shared across x86 FPU implementation files.

## Important APIs, Types, And Functions
Declares `init_fpstate`, `fpstate_init_user()`, and `fpstate_reset()`. `use_xsave()` and `use_fxsr()` wrap CPU feature checks. `WARN_ON_FPU()` expands to runtime warnings only under `CONFIG_X86_DEBUG_FPU`.

## Control Flow
There is no runtime control flow beyond inline feature tests and debug assertions.

## State, Persistence, And Dependencies
No state is defined here except external declarations. It depends on CPU feature flags and debug configuration.

## Integration Points
Included by `init.c`, `core.c`, `regset.c`, and `signal.c` to keep feature checks and debug assertions consistent.

## Risks
Changing wrappers changes feature selection throughout the FPU subsystem. Making `WARN_ON_FPU()` active or inactive affects bug visibility versus overhead.

## Test Signals
Builds should resolve declared symbols, and debug FPU builds should warn on invalid state transitions while non-debug builds compile checks away safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/legacy.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/legacy.h

## Purpose
Defines low-level legacy x87/FXSR instruction wrappers used for save/restore, signal frames, and MXCSR programming.

## Important APIs, Types, And Functions
`ldmxcsr()` loads MXCSR. `user_insn()` wraps user-memory FPU instructions with STAC/CLAC and exception tables. `kernel_insn()` and `kernel_insn_err()` wrap kernel-memory restore/save fault handling. Inline helpers include `fnsave_to_user_sigframe()`, `fxsave_to_user_sigframe()`, `fxrstor()`, `fxrstor_safe()`, `fxrstor_from_user_sigframe()`, `frstor()`, `frstor_safe()`, `frstor_from_user_sigframe()`, and `fxsave()`.

## Control Flow
Each helper selects 32-bit or 64-bit instruction variants where needed and returns either success or a trap/error code for safe restore paths. User helpers use exception table entries suitable for page fault and machine-check-safe handling.

## State, Persistence, And Dependencies
No persistent state is owned here. It depends on assembly exception table types, SMAP access toggling, FPU type definitions, and `mxcsr_feature_mask`.

## Integration Points
Used by FPU core and signal handling for non-XSAVE or FXSR-compatible paths and for direct user signal-frame save/restore.

## Risks
Exception table annotations must match the instruction fault semantics. User-memory instructions need correct access checks and fault handling to avoid corrupting FPU state or leaking kernel access.

## Test Signals
Signal frame save/restore, ptrace legacy paths, and fallback non-XSAVE CPUs should handle valid and faulting user buffers without kernel oopses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/regset.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/regset.c

## Purpose
Implements FPU user-regset get/set operations for ptrace, core dumps, 32-bit compatibility, XSAVE state, FXSR state, and CET shadow-stack pointer exposure.

## Important APIs, Types, And Functions
Active predicates include `regset_fpregs_active()`, `regset_xregset_fpregs_active()`, and `ssp_active()`. Get/set APIs include `xfpregs_get/set()`, `xstateregs_get/set()`, `fpregs_get/set()`, and `ssp_get/set()`. Conversion helpers `convert_from_fxsr()` and `convert_to_fxsr()` translate between i387 and FXSR layouts.

## Control Flow
Get paths synchronize current fpstate if needed, then copy FXSR, XSAVE, shadow-stack, or legacy i387 data into a `membuf`. Set paths reject partial/oversized writes, copy input from kernel or user buffers, validate MXCSR and xstate constraints, invalidate cached register ownership, and update fpstate memory so the target reloads it on resume. Compatibility paths convert tag words and register environments between formats.

## State, Persistence, And Dependencies
State modifications are target task fpstate memory, xsave header feature bits, target PKRU, CET user SSP, and invalidated FPU ownership. It depends on user-regset core, ptrace stop semantics, xstate copy helpers, IA32 emulation, shadow stack features, and MXCSR masks.

## Integration Points
Used by ptrace, ELF core dump generation, 32-bit compat regsets, and debugger manipulation of FPU/CET state.

## Risks
Allowing stale cached registers after ptrace modification would discard debugger writes, so invalidation is critical. Bad MXCSR, invalid SSP, or unsupported xfeatures must be rejected. 32-bit callers must not expose xmm8-15.

## Test Signals
Ptrace get/set and coredumps should round-trip FP/FX/XSAVE state, reject invalid sizes/MXCSR/SSP, clear high XMM registers for ia32 callers, and force reload after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/regset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/signal.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/signal.c

## Purpose
Saves and restores x86 FPU/xstate data in user signal frames, including legacy 32-bit layouts, XSAVE metadata, PKRU, and fault-tolerant direct user-memory operations.

## Important APIs, Types, And Functions
`copy_fpstate_to_sigframe()` writes current state to a signal frame. `fpu__restore_sig()` restores from sigreturn. `fpu__alloc_mathframe()` computes aligned frame placement. `fpu__get_fpstate_size()` reports maximum needed frame size. Helpers validate `_fpx_sw_bytes`, write magic fields, perform direct save/restore, and fold 32-bit fsave headers into FXSR data.

## Control Flow
Save first validates access, clears XSAVE header, ensures current FPU registers are loaded, attempts direct save with page faults disabled, faults in/clears user memory and retries if needed, writes 32-bit fsave headers where required, and appends XSAVE software bytes plus magic2. Restore validates frame size and optional IA32 FX layout, detects whether extended xstate is present, restores directly from user memory when possible, faults in pages on #PF, restores missing features from init state, preserves supervisor state, and clears user states on failure.

## State, Persistence, And Dependencies
State includes user signal-frame bytes, current task fpstate/register ownership, XFD state, xsave header feature bits, PKRU argument handling, and thread `TIF_NEED_FPU_LOAD`. It depends on FPU core, xstate helpers, legacy instruction wrappers, uaccess/fault-in helpers, compat signal layout, and CET/supervisor xstates.

## Integration Points
Called from signal delivery and sigreturn paths; it defines userspace ABI compatibility for old i387, FXSR, and XSAVE-aware applications.

## Risks
Signal frames are attacker-controlled on restore. The code must reject invalid magic/feature/MXCSR combinations, handle user page faults without corrupting registers, preserve supervisor xstate, and fall back to init state on failure.

## Test Signals
Signal stress should round-trip FP/SSE/AVX/PKRU/xstate data, handle 32-bit compat frames, reject malformed frames, fault safely on bad user buffers, and clear user FPU state after failed restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/signal.c -->
