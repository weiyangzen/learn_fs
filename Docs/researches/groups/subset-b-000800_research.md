# subset-b-000800 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/feature.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/feature.c

Purpose: implements the PowerMac platform feature-call layer. It discovers UniNorth/U3/U4 host bridges and mac-io chips, identifies the exact motherboard family from the device tree, maps feature selectors such as `PMAC_FTR_IDE_ENABLE`, `PMAC_FTR_USB_ENABLE`, `PMAC_FTR_SLEEP_STATE`, and `PMAC_FTR_RESET_CPU` to board-specific register sequences, and performs early power-state setup for onboard devices.

Important APIs/types/functions: exported state includes `feature_lock`, `macio_chips`, `uninorth_node`, `uninorth_base`, `macio_find`, `pmac_do_feature_call`, `pmac_feature_init`, `pmac_set_early_video_resume`, `pmac_call_early_video_resume`, `pmac_register_agp_pm`, `pmac_suspend_agp_for_card`, `pmac_resume_agp_for_card`, and `pmac_get_uninorth_variant`. Internal tables are built around `feature_table_entry`, `pmac_mb_def`, `pmac_mb_defs`, and per-family arrays such as `core99_features`, `pangea_features`, `intrepid_features`, and `g5_features`.

Control flow: `pmac_feature_init` probes the northbridge, probes mac-io controllers in order, picks a motherboard definition, then calls `set_initial_features` to put unused serial, modem, sound, Airport, FireWire, GMAC, and ATA cells into safe boot states. Runtime callers enter through `pmac_do_feature_call`, which first searches the active board feature table and then the generic table before invoking the selected handler. Handlers directly manipulate FCR, GPIO, UniNorth, U3, and K2/Shasta registers, usually under `feature_lock`, and often include readbacks plus `udelay` or `mdelay` to flush posted writes and satisfy hardware timing. Sleep handlers save register/DBDMA/GPIO state, shut down cells, program bridge power registers, and later restore them in reverse order.

State and persistence: persistent hardware state is the actual chip register state. In-memory state tracks detected motherboard metadata in `pmac_mb`, mac-io mapping and flags in `macio_chips`, UniNorth revision and variant, saved FCR/GPIO/DBDMA snapshots for sleep, early video-resume callbacks, and AGP PM callbacks. It does not persist to disk; suspend/resume correctness depends on saved static arrays and hardware registers surviving the sleep transition.

Dependencies/integration: this file is the `ppc_md.feature_call` backend used by setup, PCI, serial, network, FireWire, audio, sleep, and SMP code. It depends on Open Firmware device nodes, `macio` register macros, UniNorth/U3/U4 constants, PMU/ADB optional helpers, PCI device lookup, and low-level I2C/PMF support indirectly through other platform code.

Risks: many handlers encode board-specific timing and register knowledge with little runtime validation. A wrong motherboard match or stale device-tree compatibility string can power down or reset the wrong cell. Several paths assume `macio_chips[0]` exists and that device-id properties are present. Sleep paths save global state without per-device refcounts, and comments explicitly note missing clock refcounting. Locking covers register writes but not all flag updates, callback registration, or caller-level device lifecycle.

Test signals: boot on representative OldWorld, Core99, Pangea, Intrepid, and G5 machines or emulations; verify detected motherboard names/flags; exercise feature calls for IDE reset, SCC/modem, USB, GMAC, FireWire, Airport, sound, and CPU reset; suspend/resume with DBDMA, GPIO, FireWire cable power, GMAC WOL, and early video resume; confirm PCI probe devices are enabled during discovery and powered down afterward as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/feature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/low_i2c.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/low_i2c.c

Purpose: provides a synchronous low-level PowerMac I2C abstraction that is available earlier and with different semantics than the generic Linux I2C layer. It supports KeyWest, PMU, and SMU I2C controllers and binds selected I2C devices into the platform-function engine for firmware-described init, sleep, wake, and on-demand operations.

Important APIs/types/functions: core types are `pmac_i2c_bus`, `pmac_i2c_host_kw`, `pmu_i2c_hdr`, and `pmac_i2c_pf_inst`. Exported APIs include `pmac_i2c_find_bus`, `pmac_i2c_get_dev_addr`, `pmac_i2c_get_controller`, `pmac_i2c_get_bus_node`, `pmac_i2c_get_type`, `pmac_i2c_get_flags`, `pmac_i2c_get_channel`, `pmac_i2c_get_adapter`, `pmac_i2c_adapter_to_bus`, `pmac_i2c_match_adapter`, `pmac_i2c_open`, `pmac_i2c_close`, `pmac_i2c_setmode`, and `pmac_i2c_xfer`. Init and PM hooks are `pmac_i2c_init`, `pmac_pfunc_i2c_suspend`, and `pmac_pfunc_i2c_resume`.

Control flow: initialization probes KeyWest controllers, then PMU and SMU controllers when configured, creates `pmac_i2c_bus` objects, and registers PMF handlers for whitelisted devices such as hardware clocks, voltage controllers, and monitors. KeyWest transfers program mode, address, subaddress, and state, then either wait through interrupts/completions or poll the ISR state machine until `state_idle`. PMU transfers queue ADB requests and poll status until completion. SMU transfers queue `smu_i2c_cmd` objects and wait on a completion. PMF handlers open the bus, perform read/write/RMW/subaddress/mode commands, and close the bus at the end of each platform function.

State and persistence: all bus state is in the global `pmac_i2c_busses` list. Each bus has a mutex, current mode, open/polled flags, channel, platform device pointer, and host-specific state. KeyWest hosts have a transfer state machine, lock, timer, completion, and result fields. There is no disk persistence; the meaningful state is device register state changed by I2C writes and platform functions.

Dependencies/integration: integrates with ADB PMU, SMU, KeyLargo/UniNorth registers, OF device tree bus layout, platform devices named `i2c-powermac`, generic `i2c_adapter` exposure, and the PMF parser through `pmf_register_driver` and `pmf_do_functions`.

Risks: `pmac_i2c_force_poll` forces polling until platform devices are registered, and polling includes busy loops for timebase-frozen contexts. KeyWest uses a timer and interrupt path but is intentionally slow. PMU transfers are capped at 16 bytes and use repeated sleeps. Device-tree multibus matching depends on `reg` high bits and can skip hidden or malformed buses. RMW semantics include a device-specific inverted-mask quirk, so incorrect whitelist entries can change the wrong bits.

Test signals: probe KeyWest multibus and child-bus layouts; run standard, standard-subaddress, and combined transfers; force polled and interrupt modes; simulate NAK, timeout, and short PMU read replies; verify PMF on-init/on-sleep/on-wake for whitelisted devices; confirm platform devices expose the correct bus data and adapters match OF child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/low_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/nvram.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/nvram.c

Purpose: implements PowerMac NVRAM access for direct-mapped, indirect-addressed, PMU-backed, and Core99 flash-backed NVRAM. It wires the platform `ppc_md.nvram_*` callbacks, discovers CHRP partition offsets, and provides exported XPRAM helpers.

Important APIs/types/functions: structures include `chrp_header` and `core99_header`. Public functions are `pmac_nvram_init`, `pmac_get_partition`, `pmac_xpram_read`, and `pmac_xpram_write`. Core99 support uses `core99_nvram_read_byte`, `core99_nvram_write_byte`, `core99_nvram_read`, `core99_nvram_write`, `core99_nvram_size`, `core99_calc_adler`, `core99_check`, `core99_nvram_setup`, and `core99_nvram_sync`. Flash writers are `sm_erase_bank`, `sm_write_bank`, `amd_erase_bank`, and `amd_write_bank`.

Control flow: init locates the `nvram` OF node and its resources. Core99 flash maps two 8 KiB banks, validates signatures/checksums/Adler values, selects the bank with the highest generation, copies it into `nvram_image`, and installs buffered read/write/sync callbacks. Non-Core99 32-bit paths choose direct MMIO, indirect address/data MMIO, or PMU request based on resource count and system controller. `lookup_partitions` scans CHRP headers on NewWorld machines or uses fixed OldWorld offsets. `core99_nvram_sync` compares the shadow image to the active bank, updates generation/checksum/adler, flips banks, erases, and writes the inactive bank.

State and persistence: Core99 writes are staged in `nvram_image` and become persistent only when `nvram_sync` or `machine_shutdown` calls `core99_nvram_sync`. Direct, indirect, and PMU paths write through immediately. Global state tracks mapping count, current Core99 bank, partition offsets, flash operation callbacks, and a raw spinlock for serialized NVRAM access.

Dependencies/integration: depends on OF address parsing, memblock allocation, low-level MMIO, PMU ADB requests, `ppc_md` machine callbacks, CHRP NVRAM conventions, and exported `pmac_nvram_*` users such as time, boot settings, and XPRAM clients.

Risks: Core99 flash erase/write loops poll up to fixed software timeouts and then verify whole-bank contents. The erase/write helpers calculate `base` using `core99_bank` instead of their `bank` argument, which makes correctness depend on `core99_bank` being switched before the helper call. Debug mode adds a 2 second delay after sync. Partition scanning trusts header lengths enough to advance offsets. PMU byte access may poll when the system is not fully running.

Test signals: validate direct, indirect, PMU, and Core99 initialization; corrupt Core99 signature/checksum/adler cases; generation-bank selection; write shadow bytes then sync and verify bank flip; flash timeout and verify-failure paths; CHRP partition scanning for `common` and `APL,MacOS75`; XPRAM boundary checks and negative partition offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pci.c

Purpose: discovers and configures PowerMac PCI host bridges, supplies bridge-specific config-space accessors, applies Apple hardware fixups, and provides PowerMac PCI controller callbacks. It covers 32-bit Bandit/Chaos/Grackle/UniNorth and 64-bit U3 AGP, U3 HyperTransport, and U4 PCIe.

Important APIs/types/functions: exported or externally used symbols include `k2_skiplist`, `pmac_pci_irq_fixup`, `pmac_pci_init`, `pmac_pcibios_after_init`, and `pmac_pci_controller_ops`. Important helpers include `fixup_bus_range`, `macrisc_cfg_map_bus`, `chaos_map_bus`, `u3_ht_read_config`, `u3_ht_write_config`, `u4_pcie_cfg_map_bus`, `pmac_add_bridge`, setup functions for each bridge family, and PCI fixups for OHCI, CardBus, PCI ATA, K2 SATA, and U4 PCIe.

Control flow: `pmac_pci_init` sets global PCI flags, walks root OF children for PCI-like host bridges, creates a `pci_controller` through `pmac_add_bridge`, installs appropriate config ops, processes OF ranges, fixes bus-range properties, and performs architecture-specific post-setup. Config access paths encode type 0/type 1 cycles differently for MacRISC, U3 HT, and U4 PCIe. Device enable hooks re-enable GMAC and FireWire cells that early feature code enabled for probing and then powered down. Late fixups disable broken K2 SATA resources and repair U4 PCIe root bridge windows.

State and persistence: runtime state includes `has_uninorth`, `has_second_ohare` on 32-bit, `u3_agp` on 64-bit, global PCI flags, per-hose config address/data mappings, and `k2_skiplist` entries used to fake config reads for powered-down K2 devices. There is no persistent storage; changes are PCI config space, OF-derived resource setup, and powered-device state.

Dependencies/integration: integrates with OF PCI parsing, `pci_controller` allocation, generic PCI config helpers, PowerMac feature calls for GMAC/FireWire, IRQ mapping, DART IOMMU setup through setup code, and machine controller ops used by the generic PCI core.

Risks: many paths depend on firmware device-tree accuracy, but this file also mutates `bus-range` properties and compensates for missing or misleading nodes. U3 HT intentionally hides devices not present in OF to avoid machine checks on K2. U4 PCIe resource repair chooses the largest acceptable host memory window. 32-bit enable hooks alter command/cache-line/latency registers only for selected onboard devices; incorrect node matching can leave devices inaccessible or powered down.

Test signals: enumerate each supported bridge type; verify config reads/writes on root and subordinate buses; test U3 HT hidden/powered-down K2 devices; confirm GMAC/FireWire enable-disable lifecycle; verify second OHare IRQ fixup; CardBus and PCI ATA config rewrites; disabled firmware OHCI resource suppression; U4 PCIe bridge window programming; K2 SATA function/resource disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_base.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_base.c

Purpose: installs base platform-function handlers for mac-io GPIOs, mac-io MMIO registers, UniNorth MMIO registers, and selected UniNorth hardware-clock nodes. These handlers execute firmware-provided `platform-do-*` bytecode through the PMF core.

Important APIs/types/functions: exported lifecycle functions are `pmac_pfunc_base_install`, `pmac_pfunc_base_suspend`, and `pmac_pfunc_base_resume`. Handler tables include `macio_gpio_handlers`, `macio_mmio_handlers`, and `unin_mmio_handlers`. Key callbacks include `macio_do_gpio_irq_enable`, `macio_do_gpio_irq_disable`, `macio_do_gpio_write`, `macio_do_gpio_read`, `macio_do_write_reg32`, `macio_do_read_reg32`, `macio_do_write_reg8`, `macio_do_read_reg8`, masked/shifted read/write helpers, and `unin_do_write_reg32`.

Control flow: `pmac_pfunc_base_install` runs once for PowerMac, iterates all probed `macio_chips`, registers MMIO handlers on each mac-io node, registers GPIO handlers for every child under a `gpio` node, runs GPIO on-init functions, and registers UniNorth handlers when mapped. GPIO interrupt enable maps the node IRQ and calls `request_irq`; the IRQ handler calls `pmf_do_irq`. Register handlers apply masks under `feature_lock` and use `MACIO_IN/OUT` or `UN_IN/OUT` accessors. Suspend and resume run PMF functions with `PMF_FLAGS_ON_SLEEP` and `PMF_FLAGS_ON_WAKE` in ordered mac-io/UniNorth sequences.

State and persistence: this file adds no durable storage. PMF registration creates global PMF devices/functions in `pfunc_core.c`; `unin_hwclock` stores the optional direct-mapped hardware-clock node for later PM callbacks. Hardware register and GPIO values are the persisted platform state across calls.

Dependencies/integration: depends on `macio_chips` and `uninorth_node` from `feature.c`, `feature_lock`, PMF core registration/execution APIs, OF node walking, IRQ mapping, and mac-io/UniNorth register macros.

Risks: GPIO offsets from old-style device trees are adjusted by a hard-coded `0x50` rule. Handler driver data stores MMIO addresses as raw pointers or `macio_chip` pointers, so incorrect PMF node registration can write arbitrary platform registers. GPIO IRQ enable does not store the mapped IRQ in the function, so disable remaps it later. The file comments state that GPIO at-sleep/at-wake functions are not implemented here.

Test signals: verify PMF registration for mac-io root, GPIO children, UniNorth, and `hw-clock`; run on-init GPIO and MMIO functions; test masked writes and shifted read/write return paths; register/unregister GPIO IRQ clients and trigger `pmf_do_irq`; suspend/resume sequencing for mac-io and UniNorth functions; malformed GPIO `reg` properties and old-style offset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_core.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_core.c

Purpose: implements the platform-function bytecode parser, registry, invocation, reference management, and IRQ-client dispatch used by PowerMac device-tree `platform-do-*` properties.

Important APIs/types/functions: command parsing uses `pmf_cmd`, `pmf_next32`, `pmf_next_blob`, `pmf_parse_one`, and the `pmf_parsers` table for opcodes such as GPIO, register, I2C, config-space, delays, shifted/masked reads, shifted/masked writes, and mask-and-compare. Registry types are `pmf_device`, `pmf_function`, and `pmf_irq_client`. Exported APIs include `pmf_register_driver`, `pmf_unregister_driver`, `pmf_get_function`, `pmf_put_function`, `pmf_find_function`, `pmf_call_function`, `pmf_call_one`, `pmf_do_functions`, `pmf_register_irq_client`, `pmf_unregister_irq_client`, and `pmf_do_irq`.

Control flow: a driver registers handlers for an OF node. Registration scans all properties named `platform-do-*`, creates one or more `pmf_function` records per property, does a parse-only pass to determine each function length, and links the device into the global registry. Callers either find one on-demand function through a target node and optional phandle indirection, or run all matching functions on a registered node for a flag set such as init, sleep, wake, or interrupt generation. Invocation optionally calls a handler `begin`, parses and executes bytecode commands against the handler table, and then calls `end`.

State and persistence: global lists `pmf_devices` and per-device `functions` hold live registrations. `kref` protects device and function lifetimes, and module references protect handler owners during calls. `pmf_lock` serializes registry and IRQ-client list access; `pmf_irq_mutex` serializes IRQ enable/disable list transitions. There is no disk persistence.

Dependencies/integration: this is the common engine used by `pfunc_base.c`, `low_i2c.c`, device drivers that consume platform functions, OF property/phandle lookup, and module ownership. Handler behavior is supplied by the registering subsystem, so PMF core is intentionally transport-agnostic.

Risks: file comments call out incomplete race-free locking. `pmf_do_irq` holds the spinlock while invoking client handlers, so handlers must be IRQ-safe and bounded. Parse-only and execute passes depend on correct bytecode length calculation; malformed properties return `-ENXIO` and may stop adding later functions. Several opcodes are unimplemented. `pmf_call_one` calls `end` even if `begin` fails and returns `NULL`, relying on handlers to tolerate that.

Test signals: register drivers with multiple `platform-do-*` functions; malformed/truncated bytecode and unknown opcodes; phandle-directed function lookup; flag filtering for on-init/on-sleep/on-wake/on-demand/interrupt; begin/end lifecycle on success and failure; module refcount behavior; IRQ client first-enable/last-disable and dispatch under concurrent registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pic.c

Purpose: initializes and operates PowerMac interrupt controllers. It supports old 32-bit Apple PIC variants in Grand Central, OHare, Heathrow/Gatwick, and newer MPIC/OpenPIC controllers, including BootX and OldWorld interrupt-map workarounds and sleep-time interrupt masking.

Important APIs/types/functions: key globals are `of_irq_workarounds`, `of_irq_dflt_pic`, `pmac_irq_hw`, `ppc_lost_interrupts`, `ppc_cached_irq_mask`, `pmac_irq_cascade`, and `pmac_pic_host`. Public entry points are `pmac_pic_init` and, on old 32-bit systems, `of_irq_parse_oldworld`. Old PIC operations are `pmac_startup_irq`, `pmac_mask_irq`, `pmac_unmask_irq`, `pmac_ack_irq`, `pmac_mask_and_ack_irq`, `pmac_retrigger`, and `pmac_pic_get_irq`. MPIC setup uses `pmac_setup_one_mpic` and `pmac_pic_probe_mpic`.

Control flow: `pmac_pic_init` configures OF IRQ parser workarounds, tries MPIC discovery first, and falls back to old-style PIC probing on 32-bit. Old-style probing determines the master/slave controller layout from OF nodes, creates a linear irq domain, maps controller registers, disables all interrupts, wires cascade handling for Gatwick/second controllers, and installs `ppc_md.get_irq`. Interrupt dispatch scans enabled event, level, and software-lost bits from high to low controller words, maps hardware IRQs through the domain, and returns Linux IRQs. Masking and unmasking update cached masks under a raw spinlock and retrigger level interrupts that were already asserted.

State and persistence: in-memory bitmaps cache enabled interrupts and lost interrupts; hardware enable/ack/level/event registers hold controller state. Suspend saves primary controller masks in `sleep_save_mask`, disables all but the PMU VIA wake interrupt, and resume restores masks by unmasking saved IRQs.

Dependencies/integration: integrates with Linux irq domains, generic irq chips, MPIC allocation/init, OF IRQ parsing, PMU VIA wake discovery, XMON NMI hooks, PowerMac feature calls for MPIC enable, and machine `ppc_md.get_irq`.

Risks: old PIC code assumes a maximum of 128 interrupts and specific register layouts. `pmac_pic_probe_oldstyle` prints `%pOF` after `of_node_put(master)`, which is only safe if the node lifetime remains valid. Lost-interrupt retriggering uses decrementer kicks and cached bitmaps, so mask races can produce duplicate or delayed handling if ordering changes. BootX missing-phandle workarounds rely on best-effort default controller selection.

Test signals: boot with MPIC and old PIC hardware; single and cascaded controller layouts; edge and level startup behavior; retrigger of asserted level lines; lost-interrupt accounting; OldWorld `AAPL,interrupts` parsing through PCI parent fallback; BootX no-phandle default PIC detection; XMON NMI registration; suspend/resume with PMU VIA wake interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pmac.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pmac.h

Purpose: declares cross-file PowerMac platform interfaces used by the local `pmac_*` implementation files. It is the internal header that ties setup, PCI, NVRAM, interrupt, feature, time, DMA, and SMP support together.

Important APIs/types/functions: declarations include `pmac_newworld`, `g5_phy_disable_cpu1`, time/RTC functions, `pmac_pci_irq_fixup`, `pmac_pci_init`, `pmac_nvram_update`, `pmac_nvram_read_byte`, `pmac_nvram_write_byte`, `pmac_pcibios_after_init`, `pmac_setup_pci_dma`, `pmac_check_ht_link`, `pmac_setup_smp`, `psurge_secondary_virq`, `low_cpu_offline_self`, `pmac_nvram_init`, `pmac_pic_init`, and `pmac_pci_controller_ops`.

Control flow: this file has no executable control flow. Its role is compile-time integration: `setup.c` pulls in platform entry points, `pci.c` exposes controller ops and IRQ fixup, `pic.c` exposes interrupt initialization, `nvram.c` exposes NVRAM setup, and `sleep.S` exposes `low_cpu_offline_self` for SMP/hotplug and sleep flows.

State and persistence: it declares shared state but owns none. The main stateful declaration is `pmac_newworld`, which affects setup, NVRAM partition lookup, and IRQ parsing policy. Persistence behavior comes from the implementation files.

Dependencies/integration: includes Linux PCI and IRQ headers plus `asm/pmac_feature.h`, so users get the platform feature-call selector context. It forward-declares `struct rtc_time` to avoid pulling RTC internals into every platform source.

Risks: as an internal header, mismatches between declarations and implementations can break platform initialization at link or runtime. Conditional definitions in implementation files mean some declarations only resolve for relevant config combinations. `low_cpu_offline_self` is marked `noreturn`; callers must treat it as terminal.

Test signals: build coverage across PPC32/PPC64, SMP/non-SMP, PM/no-PM, NVRAM enabled/disabled, and PCI configs; link verification for all declared symbols; boot smoke tests that exercise the `define_machine(powermac)` callbacks declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/setup.c

Purpose: defines the PowerMac machine descriptor and early platform setup. It detects PowerMac compatibility, initializes chipset features, NVRAM, interrupt and PCI callbacks, CPU/cache settings, default root selection, restart/poweroff paths, OF platform devices, and `/proc/cpuinfo` reporting.

Important APIs/types/functions: important symbols include `pmac_newworld`, exported `sys_ctrler`, `pmac_show_cpuinfo`, fallback `find_via_cuda`, `find_via_pmu`, `smu_init`, `pmac_setup_arch`, `pmac_late_init`, `note_bootable_part`, `pmac_restart`, `pmac_power_off`, `pmac_halt`, `pmac_init`, `pmac_declare_of_platform_devices`, `check_pmac_serial_console`, `pmac_probe`, and `define_machine(powermac)`.

Control flow: `pmac_probe` checks OF compatibility, sets DMA mode constants on 32-bit, installs `pm_power_off`, and calls `pmac_init`. `pmac_init` optionally enables early debug, runs `pmac_feature_init`, initializes udbg backends, performs DART early setup on PPC64, and sets up SMP early. `pmac_setup_arch` computes provisional `loops_per_jiffy`, detects NewWorld by interrupt-controller presence, initializes OHare/L2 cache on PPC32, probes CUDA/PMU/SMU, initializes NVRAM, selects a default root device on PPC32, and honors `adb_sync`. The machine descriptor then wires setup, PCI discovery, IRQ init, time, RTC, restart, halt, feature calls, and platform-specific PCI post-init hooks into the PowerPC core.

State and persistence: tracks `has_l2cache`, `pmac_newworld`, `current_root_goodness`, and `initializing`. `note_bootable_part` mutates `ROOT_DEV` only during initialization and only if the command line lacks `root=`. Power-off/restart state is delegated to CUDA, PMU, or SMU controllers. No file-backed persistence is performed here.

Dependencies/integration: depends on OF tree queries, `pmac_feature_init`, NVRAM, PCI, PIC, time/RTC code, ADB CUDA/PMU/SMU subsystems, btext/udbg console code, IOMMU/DART, SMP setup, and Linux machine descriptor registration.

Risks: setup order is critical: feature probing precedes PCI and IRQ setup, SMP runs before interrupt stack allocation, and NVRAM setup depends on controller detection. Fallback stubs for disabled CUDA/PMU/SMU only warn or no-op, so unsupported kernels may hang on restart/poweroff. `note_bootable_part` can change root selection based on device discovery order and goodness while initialization is still true.

Test signals: boot detection for `Power Macintosh` and `MacRISC`; NewWorld vs OldWorld detection; `/proc/cpuinfo` fields; root-device override behavior with and without `root=`; CUDA, PMU, and SMU restart/poweroff paths; early serial console selection from `linux,stdout-path`; OF platform-device creation for video, SMU, and fan controller nodes; build/boot across PPC32/PPC64 and SMP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/sleep.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/sleep.S

Purpose: contains low-level 32-bit Book3S PowerMac sleep, wake, and CPU-offline assembly. It saves processor state before PMU-triggered sleep, installs ROM wake vectors, disables caches and translation, enters HID0 sleep, and restores CPU/MMU state on wake.

Important APIs/types/functions: exported labels are `low_sleep_handler`, `low_cpu_offline_self`, and `core99_wake_up`; local resume label is `grackle_wake_up`. The `sleep_storage` BSS block uses `SL_*` offsets to store stack pointer, resume PC, MSR, SDR1, SPRGs, BATs, timebase, TOC, CR, LR, and r12-r31. It calls shared low-level helpers such as `__save_cpu_setup`, `flush_disable_caches`, `load_segment_registers`, `__restore_cpu_setup`, `reloc_offset`, `__init_fpu_registers`, and `__inval_enable_L1`.

Control flow: when configured for PM, CPU frequency, or hotplug, `low_sleep_handler` saves volatile return state, callee-saved registers, MSR, SDR1, timebase, SPRGs, normal BATs, and high BATs when supported. It saves CPU setup, writes OldWorld/PowerBook wake information at physical address 0/4 using the `Lars` magic, writes Core99 wake vector data at physical addresses 0x80/0x84, then falls through to `low_cpu_offline_self`. CPU offline flushes and disables caches, disables data relocation, applies a 7450 workaround when needed, sets HID0 sleep, sets MSR POW, and loops sleeping. `core99_wake_up` sanitizes HID0/MSR, locates physical `sleep_storage`, then resumes through `grackle_wake_up`, which restores segment registers, CPU setup, FPU state, L1 cache, SDR1, SPRGs, BATs, TLBs, timebase, CR, TOC, saved GPRs, stack, SRR0/SRR1, and returns with `rfi`.

State and persistence: state is preserved only in `sleep_storage` and in fixed low physical wake-vector locations consumed by ROM/firmware. Hardware state includes HID0, MSR, BATs, SDR1, SPRGs, TLBs, and timebase. There is no external persistence.

Dependencies/integration: called by PMU sleep flows, CPU frequency code, and 32-bit CPU hotplug paths. It depends on PowerPC assembly macros, MMU feature fixup sections, CPU feature fixups, kernel physical mapping assumptions, and firmware wake-vector conventions for Grackle/older and Core99 machines.

Risks: this code runs with caches, translation, and normal kernel services unavailable. Wrong physical addresses, missing cache flushes, or incomplete BAT/SPR restoration can prevent resume. It is compiled out for non-Book3S-32. The sleep loop intentionally never returns except through firmware wake, so accidental calls are terminal. Fixed low-memory wake-vector writes must not conflict with other early-resume users.

Test signals: suspend/resume on Wallstreet/Lombard and Core99 systems; CPU hotplug/offline on PPC32; high-BAT CPUs with `MMU_FTR_USE_HIGH_BATS`; 7450 cache workaround paths; timebase continuity after resume; TLB/BAT restoration under memory above 256 MiB; build coverage with PM, CPU frequency, hotplug, and non-Book3S configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/sleep.S -->
