# subset-b-001072 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ti-sysc.c -->
## sources/distributed-fs/ceph-client/drivers/bus/ti-sysc.c

### Purpose
`ti-sysc.c` is the Texas Instruments interconnect target wrapper driver. It discovers a module wrapper from devicetree, maps its revision/SYSCONFIG/SYSSTATUS registers, manages clocks and reset lines, configures idle and standby modes, applies SoC/module quirks, and then populates the child devices behind the wrapper.

### Important APIs, Types, And Functions
The central state is `struct sysc`, which stores register offsets, mapped module base, clocks, reset control, capabilities, runtime PM state, saved `sysconfig`, and quirk callbacks. `struct sysc_capabilities`, `struct sysc_regbits`, and the OF match table describe register layouts for OMAP2, OMAP4, timers, SmartReflex, McASP, USB host, MCAN, and PRUSS variants. Key flows are `sysc_probe()`, `sysc_init_module()`, `sysc_runtime_resume()`, `sysc_runtime_suspend()`, `sysc_reset()`, `sysc_enable_module()`, `sysc_disable_module()`, and `of_platform_populate()` of children.

### Control Flow
Probe allocates `struct sysc`, initializes global SoC data, reads match data and DT quirks, parses child ranges and named register resources, maps the register window, parses masks and idle modes, initializes legacy platform data, applies early address/register quirks, skips disabled or reserved modules, gets/prepares clocks, gets optional reset control, and initializes the hardware. Module initialization denies clockdomain idle, enables optional and main clocks, optionally deasserts reset, reads revision, applies revision quirks, runs legacy init if needed, enables the module, and optionally soft-resets it. After runtime PM is enabled, children are populated unless the module is reserved; delayed work later balances clocks/runtime references for no-idle or no-reset-on-init cases.

### State And Persistence
Persistent hardware state is the wrapper register programming: idle modes, reset state, clocks, and child device availability. Driver state includes `ddata->enabled`, saved `sysconfig` for context-loss detection, delayed idle work, and SoC-global disabled/restored module lists protected by `sysc_soc->list_lock`. Context-loss recovery may re-enable, reset, and restore `sysconfig` via a CPU PM notifier for modules tagged with `SYSC_QUIRK_REINIT_ON_CTX_LOST`.

### Dependencies And Integration Points
The driver integrates with OF address parsing, platform bus population, clk and clkdev, reset controller, PM runtime, generic PM domains through parent buses, CPU PM notifiers, and legacy `ti_sysc_platform_data` callbacks. A platform bus notifier adds parent clocks to child devices as they appear. It also consumes TI devicetree binding flags such as `ti,sysc-mask`, `ti,syss-mask`, `ti,sysc-midle`, `ti,sysc-sidle`, and no-idle/no-reset quirks.

### Risks And Edge Cases
Register-offset validation is critical because this driver can touch wrapper registers before children bind. Quirk detection relies on base address, offsets, and revision masks; stale DT data can select wrong reset or idle behavior. Runtime PM sequencing must keep clockdomain idle denied while clocks/registers are being manipulated. The delayed idle path intentionally leaves modules active for early console or no-reset cases and must balance usage counts exactly once. Reset polling has special handling when timekeeping is suspended. The DSS, I2C, RTC, watchdog, OTG, SGX, and PRUSS quirks write child/module-specific registers, so regressions can be hardware-specific and hard to catch in generic boot tests.

### Test Signals
Useful signals are successful boot and child population on representative OMAP/AM/DRA SoCs, runtime suspend/resume cycles for child devices, system suspend/resume with context loss, CPU cluster idle exit on AM335x GPMC/OTG, correct early console behavior with no-idle/no-reset flags, DT validation for register ranges and clock names, and absence of reset timeout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ti-sysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ts-nbus.c -->
## sources/distributed-fs/ceph-client/drivers/bus/ts-nbus.c

### Purpose
`ts-nbus.c` implements the Technologic Systems NBUS used by TS-4600 boards to communicate with FPGA peripherals over GPIO lines and a PWM-driven FPGA clock.

### Important APIs, Types, And Functions
`struct ts_nbus` owns the PWM, eight data GPIO descriptors, control GPIOs (`csn`, `txrx`, `strobe`, `ale`, `rdy`), and a mutex. Exported APIs `ts_nbus_read()` and `ts_nbus_write()` provide 16-bit register access for child drivers. Probe gathers GPIOs with devm GPIO APIs, configures the PWM, stores the bus instance as drvdata, and populates child platform devices.

### Control Flow
Read and write operations take the mutex for atomic bus access. Reads set TX/RX to read mode, write the address with ALE asserted, switch data GPIOs to input, then read two bytes MSB-first while checking `rdy`. Writes set TX/RX to write mode, write the address, write two value bytes MSB-first, then pulse `csn` until `rdy` reports completion. Probe initializes GPIOs, enables the PWM at full duty cycle, and calls `of_platform_populate()` so child devices can use the exported bus helpers.

### State And Persistence
State is mostly physical line state plus the PWM enable state. The driver persists no register cache; each operation bit-bangs the bus. Removal disables the PWM under the same mutex to stop the FPGA-facing clock.

### Dependencies And Integration Points
The driver depends on devicetree GPIO names `ts,data`, `ts,csn`, `ts,txrx`, `ts,strobe`, `ts,ale`, `ts,rdy`, a PWM provider, and `linux/ts-nbus.h` consumers. Child devices use the parent drvdata and exported GPL symbols to access FPGA registers.

### Risks And Edge Cases
The read path loops while `rdy` is nonzero and the write path spins until `rdy` clears without timeout, so broken hardware or GPIO wiring can hang callers. GPIO array ordering must match bit order. Direction changes around reads must be restored to output even on errors. PWM period validation catches an unusable PWM state, but runtime PWM failures after probe are not retried.

### Test Signals
Probe should log initialization and populate expected children. Hardware tests should cover repeated reads/writes, wrong-address behavior, concurrent child access, PWM disable on remove, GPIO error injection, and a wedged `rdy` line to expose lack of timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/ts-nbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/uniphier-system-bus.c -->
## sources/distributed-fs/ceph-client/drivers/bus/uniphier-system-bus.c

### Purpose
`uniphier-system-bus.c` programs the Socionext UniPhier System Bus Controller chip-select windows from devicetree ranges and then instantiates child devices on the configured external bus.

### Important APIs, Types, And Functions
`struct uniphier_system_bus_priv` stores the MMIO base and eight `uniphier_system_bus_bank` ranges. `uniphier_system_bus_add_bank()` normalizes and validates ranges, `uniphier_system_bus_check_overlap()` rejects overlapping banks, `uniphier_system_bus_check_boot_swap()` swaps CS0/CS1 configuration when hardware boot swap is active, and `uniphier_system_bus_set_reg()` writes SBC base registers.

### Control Flow
Probe maps the controller registers, parses OF ranges, converts each range's high bus address bits to a bank number, rounds physical windows to hardware granularity, rejects duplicates and overlaps, handles boot swap, writes all bank enable/mask registers, saves drvdata, and calls `of_platform_default_populate()`. Resume simply rewrites the saved bank register values.

### State And Persistence
The computed bank table is kept in driver memory and re-applied after system sleep. Hardware-visible state is the SBC_BASE register set. Unused bank 0/1 entries are written as `0xffffffff` rather than disabled because the hardware routes accesses oddly when those entries are zero.

### Dependencies And Integration Points
The file depends on OF range parsing, platform MMIO mapping, and the child devices below the bus node. The devicetree range encoding must carry the bank number in the upper 32 bits of `range.bus_addr`.

### Risks And Edge Cases
Window rounding can expand ranges, so overlap checks after normalization are essential. Addresses above 32 bits are rejected. Boot-swap handling changes bank assignment based on live hardware state, so tests need real boot modes. Resume assumes the saved bank table remains valid and no firmware reconfiguration must be merged.

### Test Signals
Test by booting with populated ranges, empty banks, duplicate banks, overlapping windows, bank numbers over seven, boot-swap on/off, and suspend/resume. Child devices should only probe after the bus windows are programmed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/uniphier-system-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/vexpress-config.c -->
## sources/distributed-fs/ceph-client/drivers/bus/vexpress-config.c

### Purpose
`vexpress-config.c` exposes ARM Versatile Express SYS_CFG functions as regmaps for devices below the vexpress config bus. It builds SYS_CFGCTRL command templates from devicetree topology properties and serializes register-like reads/writes through the board's configuration controller.

### Important APIs, Types, And Functions
`struct vexpress_syscfg` owns the SYS_CFG MMIO base and list of active function regmaps. `struct vexpress_syscfg_func` stores command templates and its regmap. `devm_regmap_init_vexpress_config()` is the exported consumer API. `vexpress_syscfg_exec()` performs one command, `vexpress_syscfg_regmap_init()` parses `arm,vexpress-sysreg,func`, and `vexpress_syscfg_probe()` maps the controller, determines the master site, validates optional HBI data, and populates config-bus children.

### Control Flow
Consumers call `devm_regmap_init_vexpress_config()` from a child device. The bridge init path resolves site/position/dcc inherited from devicetree, handles `VEXPRESS_SITE_MASTER`, parses pairs of function/device numbers, creates one SYS_CFGCTRL template per index, and initializes a regmap with custom read/write callbacks. Reads and writes acquire the shared mutex through regmap config, write data and command registers, then poll SYS_CFGSTAT until COMPLETE, ERR, timeout, or signal interruption.

### State And Persistence
The current master site is global. Per-consumer state persists in `vexpress_syscfg_func` until the devres cleanup calls `vexpress_syscfg_regmap_exit()`. Hardware state is transient command execution; persistent values live in the platform configuration registers behind SYS_CFG.

### Dependencies And Integration Points
The driver depends on platform MMIO resources, OF properties `arm,vexpress,site`, `arm,vexpress,position`, `arm,vexpress,dcc`, `arm,vexpress-sysreg,func`, and `arm,vexpress,config-bridge`, plus Linux regmap. It integrates with other vexpress drivers that need syscfg-backed regmaps.

### Risks And Edge Cases
The shared regmap config's `max_register` is mutated during each regmap init, which is safe only because init is serialized by probe/devres assumptions rather than per-instance config allocation. `vexpress_syscfg_exec()` can sleep unless interrupts are disabled, then falls back to `udelay`; callers in atomic contexts still risk long busy waits. The energy function compatibility quirk rewrites one legacy function into two templates. `vexpress_syscfg_regmap_exit()` deletes `&syscfg->funcs` rather than `&func->list`, which is suspicious and worth review.

### Test Signals
Exercise regmap reads/writes for multiple child functions, signal interruption during a long command, SYS_CFGSTAT error and timeout paths, HBI mismatch warnings, legacy `arm,vexpress-energy` nodes, and multiple children registering/releasing regmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bus/vexpress-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/cache/Kconfig

### Purpose
This Kconfig file defines cache-maintenance driver options for noncoherent DMA and memory-hotplug-like coherency operations.

### Important APIs, Types, And Functions
It introduces `CACHEMAINT_FOR_DMA`, `AX45MP_L2_CACHE`, `SIFIVE_CCACHE`, `STARFIVE_STARLINK_CACHE`, `CACHEMAINT_FOR_HOTPLUG`, and `HISI_SOC_HHA`. The symbols select or depend on architecture features such as `RISCV`, `RISCV_NONSTANDARD_CACHE_OPS`, `RISCV_DMA_NONCOHERENT`, `GENERIC_CPU_CACHE_MAINTENANCE`, `ARM64`, and `ACPI`.

### Control Flow
Menu visibility is split into two groups. RISC-V noncoherent DMA cache-maintenance drivers are enabled under `CACHEMAINT_FOR_DMA`, which defaults to yes on RISC-V. The HiSilicon HHA driver is visible under `CACHEMAINT_FOR_HOTPLUG` when generic CPU cache maintenance is available.

### State And Persistence
The file contributes build-time configuration only. It indirectly controls whether cache operation registration code is built into the kernel or as a module.

### Dependencies And Integration Points
The Kconfig choices feed `drivers/cache/Makefile` and decide whether platform-specific cache maintenance objects are compiled. Selections are important because the corresponding C files register with RISC-V nonstandard cache ops or the generic cache coherency framework.

### Risks And Edge Cases
Overbroad defaults can build platform drivers on systems with no matching hardware, but early init/probe paths generally return `-ENODEV`. Missing `select` dependencies would produce link errors or disabled registration paths. `SIFIVE_CCACHE` is limited to SiFive and StarFive architectures while compatible strings include additional SoCs, so portability depends on architecture Kconfig coverage.

### Test Signals
Configuration tests should build all symbols enabled, all disabled, module build for `HISI_SOC_HHA`, COMPILE_TEST coverage, and RISC-V kernels with each nonstandard cache driver individually selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/Makefile -->
## sources/distributed-fs/ceph-client/drivers/cache/Makefile

### Purpose
The Makefile maps cache-maintenance Kconfig symbols to their driver objects.

### Important APIs, Types, And Functions
It builds `ax45mp_cache.o`, `sifive_ccache.o`, `starfive_starlink_cache.o`, and `hisi_soc_hha.o` from the corresponding `CONFIG_*` symbols.

### Control Flow
Kbuild includes an object only when its symbol is enabled. `HISI_SOC_HHA` may be built as a module because the Kconfig symbol is tristate; the RISC-V cache controller entries are bool options in this tree.

### State And Persistence
There is no runtime state. The file affects the kernel image or module set produced by a build.

### Dependencies And Integration Points
The object names correspond directly to source files in `drivers/cache` and to symbols declared in `Kconfig`.

### Risks And Edge Cases
The main risks are stale object mappings after file renames, mismatched symbol names, or expecting modular builds for bool-only entries. Build coverage across configurations is the best guard.

### Test Signals
Run Kbuild with each relevant `CONFIG_*` enabled and disabled, including `CONFIG_HISI_SOC_HHA=m`, and verify expected objects or modules are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/ax45mp_cache.c -->
## sources/distributed-fs/ceph-client/drivers/cache/ax45mp_cache.c

### Purpose
`ax45mp_cache.c` registers software cache-management operations for Andes AX45MP systems that need nonstandard cache maintenance for noncoherent DMA.

### Important APIs, Types, And Functions
`struct ax45mp_priv` stores the L2 controller MMIO base and cache line size. `ax45mp_cpu_cache_operation()` performs per-line L1 CSR and L2 MMIO operations. `ax45mp_dma_cache_inv()`, `ax45mp_dma_cache_wback()`, and `ax45mp_dma_cache_wback_inv()` implement `struct riscv_nonstd_cache_ops`. `ax45mp_cache_init()` is an `early_initcall`.

### Control Flow
Early init finds an `andestech,ax45mp-cache` node, skips unavailable hardware, maps the L2 controller resource, validates `cache-line-size`, and registers nonstandard RISC-V cache ops if `riscv_cbom_block_size` indicates software handling is needed. Each DMA op converts the physical address to a virtual address, aligns the range to the line size, disables local interrupts, walks cache lines, issues L1 CCTL CSRs, writes physical line addresses and commands to per-hart L2 registers, and busy-waits for the per-hart status bits to become idle.

### State And Persistence
State is global and singleton: the mapped L2 base, expected 64-byte line size, and registered RISC-V cache ops. There is no unregistration path because this is early platform setup.

### Dependencies And Integration Points
The driver depends on OF address translation, Andes-specific CCTL CSRs, L2 controller register layout, `phys_to_virt()` reachability, `smp_processor_id()`, and `riscv_noncoherent_register_cache_ops()`.

### Risks And Edge Cases
The busy-wait loop has no timeout. Operations assume hart IDs map directly to L2 per-core register slots. Interrupts are disabled during potentially large range walks, which can affect latency. `wback_inv` is implemented as writeback then invalidate, doubling walk cost. If `cache-line-size` differs from 64 bytes, init fails rather than adapting.

### Test Signals
Boot on AX45MP with and without IOCP/CBOM support, DMA correctness tests for unaligned buffers, stress large DMA ranges, CPU hotplug or SMP hart-id coverage, and instrumentation for stuck L2 status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/ax45mp_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/hisi_soc_hha.c -->
## sources/distributed-fs/ceph-client/drivers/cache/hisi_soc_hha.c

### Purpose
`hisi_soc_hha.c` exposes HiSilicon Hydra Home Agent cache clean-invalidate support through the generic cache coherency operations framework.

### Important APIs, Types, And Functions
`struct hisi_soc_hha` embeds `struct cache_coherency_ops_inst` first, plus a mutex and MMIO base. `hisi_soc_hha_wbinv()` starts a range clean-invalidate operation, `hisi_soc_hha_done()` waits for completion, and `hisi_soc_hha_probe()` allocates/registers an operation instance for ACPI ID `HISI0511`.

### Control Flow
Probe allocates the coherency instance, maps the HHA MMIO resource, initializes the mutex, and registers with `cache_coherency_ops_instance_register()`. `wbinv` rejects zero sizes, aligns the address and top to 128-byte granules, waits for any previous operation to finish, writes start and length registers, programs clean-invalidate range mode, and returns immediately after starting. `done` locks the same instance and polls until the enable bit clears or times out.

### State And Persistence
Each platform device has its own registered coherency instance and MMIO mapping. Hardware state is an in-flight range maintenance operation. The mutex serializes overlapping commands per HHA instance.

### Dependencies And Integration Points
The file imports the `CACHE_COHERENCY` namespace and depends on ACPI platform enumeration, MMIO resources, `readl_poll_timeout_atomic()`, and the generic `cache_coherency_ops` API used by hotplug-like cache maintenance flows.

### Risks And Edge Cases
The driver intentionally does not filter physical addresses to the HHA responsible for a line; every instance may receive the operation and hardware must report success if not responsible. Polling is atomic and bounded to 50 ms. Size is programmed as inclusive `size - 1`, so alignment and underflow handling are critical. Remove must unregister before unmapping to avoid callbacks into freed MMIO.

### Test Signals
Test ACPI probe/remove, multi-HHA systems, zero-size rejection, unaligned ranges, concurrent `wbinv` calls, timeout on a forced busy bit, and full hotplug/cache-maintenance users that call both start and done.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/hisi_soc_hha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/sifive_ccache.c -->
## sources/distributed-fs/ceph-client/drivers/cache/sifive_ccache.c

### Purpose
`sifive_ccache.c` supports SiFive-compatible composable cache controllers, including ECC interrupt reporting, cacheinfo private attributes, optional debugfs ECC injection, and nonstandard cache flush operations for some RISC-V SoCs.

### Important APIs, Types, And Functions
Global state includes `ccache_base`, ECC IRQ numbers, cacheinfo ops, and cache level. `sifive_ccache_init()` maps the controller and registers cacheinfo/nonstandard ops. `sifive_ccache_probe()` requests ECC IRQs. `ccache_int_handler()` handles correctable and uncorrectable directory/data ECC events. `register_sifive_ccache_error_notifier()` and `unregister_sifive_ccache_error_notifier()` export an atomic notifier chain.

### Control Flow
Architecture init finds a matching cache node, maps registers, reads `cache-level`, optionally registers nonstandard cache ops for compatible strings with the quirk, prints configuration, installs cacheinfo private attributes, optionally creates debugfs injection controls, and registers the platform driver. Platform probe counts IRQs and requests each ECC interrupt, skipping broken DATA_UNCORR where marked. Interrupt handling reads address/count registers, clears the interrupt by reading count, notifies listeners, and panics on directory uncorrectable errors while only logging/notifying data uncorrectable errors.

### State And Persistence
The driver uses singleton global state for the mapped controller and cache level. ECC counts persist in hardware registers until read. `number_of_ways_enabled` exposes live WAYENABLE state via sysfs cacheinfo private attributes. Debugfs can persist as long as the driver is loaded.

### Dependencies And Integration Points
It depends on OF compatible data, platform IRQs, RISC-V cacheinfo hooks, optional `CONFIG_RISCV_NONSTANDARD_CACHE_OPS`, optional debugfs, and the exported SiFive cache error notifier API used by other kernel consumers.

### Risks And Edge Cases
The singleton design assumes one relevant cache controller. Nonstandard flush writes one line at a time with memory barriers before and after; large ranges can be expensive. IRQ array indexing assumes the hardware IRQ order matches the enum. The DATA_UNCORR quirk hides one broken interrupt. Directory uncorrectable ECC intentionally panics, so false IRQ mapping is severe. Debugfs injection validates only numeric ranges, not platform safety.

### Test Signals
Boot with each compatible string, verify cacheinfo `number_of_ways_enabled`, trigger correctable and uncorrectable ECC paths where safe, test notifier registration/unregistration, exercise nonstandard flush on DMA workloads, and validate debugfs injection only under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/sifive_ccache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/starfive_starlink_cache.c -->
## sources/distributed-fs/ceph-client/drivers/cache/starfive_starlink_cache.c

### Purpose
`starfive_starlink_cache.c` registers StarFive StarLink cache controller operations for RISC-V noncoherent DMA cache maintenance.

### Important APIs, Types, And Functions
The file has a singleton `starlink_cache_base`. `starlink_cache_dma_cache_wback()`, `starlink_cache_dma_cache_invalidate()`, and `starlink_cache_dma_cache_wback_inv()` write controller range registers and command modes. `starlink_cache_flush_complete()` polls for completion. `starlink_cache_init()` performs OF discovery and registration.

### Control Flow
Arch init finds an available `starfive,jh8100-starlink-cache` node, reads and validates `cache-block-size`, maps the controller, sets `riscv_cbom_block_size`, marks noncoherent support, and registers nonstandard cache ops. Each operation writes start and end physical addresses masked to 40 bits, issues a memory barrier, writes the flush control mode, and polls until the enable bit clears.

### State And Persistence
State is global MMIO mapping plus registered RISC-V cache ops. Hardware state is transient per range flush/invalidate commands. There is no explicit unmap or unregister path for this arch init driver.

### Dependencies And Integration Points
The driver depends on OF, 64-bit RISC-V, noncoherent DMA infrastructure, 64-bit MMIO accesses, and a block size that is a multiple of 64 bytes. It integrates directly with the DMA cache maintenance callbacks used by noncoherent devices.

### Risks And Edge Cases
The code writes the mode field without explicitly setting an enable bit; this relies on hardware semantics where the mode write starts the operation. The end address is `paddr + size` rather than an explicitly inclusive endpoint, so it must match the controller contract. Completion timeout is long, five seconds, and only warns on failure. Address masking limits ranges to 40-bit physical addresses.

### Test Signals
Boot on JH8100 hardware, DMA correctness for clean, invalidate, and clean-invalidate paths, unaligned and zero-size ranges, high physical addresses near the 40-bit mask, timeout injection, and validation that the configured cache block size matches DMA expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cache/starfive_starlink_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/Makefile -->
## sources/distributed-fs/ceph-client/drivers/cdrom/Makefile

### Purpose
The cdrom Makefile selects the uniform CD-ROM core and GD-ROM driver objects from Kconfig symbols.

### Important APIs, Types, And Functions
`obj-$(CONFIG_CDROM) += cdrom.o` builds the uniform CD-ROM layer. `obj-$(CONFIG_GDROM) += gdrom.o` builds the GD-ROM driver.

### Control Flow
Kbuild includes each object when its configuration symbol is enabled. The uniform layer can be built into the kernel or as a module depending on `CONFIG_CDROM`.

### State And Persistence
There is no runtime state; it affects build outputs only.

### Dependencies And Integration Points
The mapping is used by low-level optical drivers that link against exported symbols in `cdrom.o`.

### Risks And Edge Cases
Build failures would occur if `CONFIG_GDROM` or `CONFIG_CDROM` are enabled but the corresponding source or exported dependencies are missing. Because many drivers use the uniform layer, accidental omission of `cdrom.o` breaks broad optical-drive functionality.

### Test Signals
Build with `CONFIG_CDROM=y/m`, with `CONFIG_GDROM` enabled, and with CD-ROM disabled to verify expected objects are included or omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/cdrom.c -->
## sources/distributed-fs/ceph-client/drivers/cdrom/cdrom.c

### Purpose
`cdrom.c` is the Linux uniform CD-ROM layer. It provides common registration, open/release policy, media-change handling, audio and MMC/DVD ioctl handling, writable media probing, changer support, and `/proc/sys/dev/cdrom` sysctl reporting for low-level optical drivers.

### Important APIs, Types, And Functions
Low-level drivers register a `struct cdrom_device_info` and `struct cdrom_device_ops` via `register_cdrom()` and remove it with `unregister_cdrom()`. Exported helpers include `cdrom_open()`, `cdrom_release()`, `cdrom_ioctl()`, `cdrom_check_events()`, `cdrom_get_media_event()`, `cdrom_number_of_slots()`, `init_cdrom_command()`, `cdrom_mode_sense()`, `cdrom_mode_select()`, `cdrom_multisession()`, `cdrom_read_tocentry()`, `cdrom_get_last_written()`, and `cdrom_probe_write_features()`. Internal command routing is split across `open_for_data()`, `media_changed()`, `dvd_do_auth()`, `dvd_read_struct()`, `mmc_ioctl()`, and many small ioctl helpers.

### Control Flow
Registration validates required low-level open/release methods, initializes default options from module parameters, propagates write capability to the block disk read-only flag, and adds the device to `cdrom_list`. Normal data opens increment `use_count`, optionally close the tray, verify media status and track types, call the low-level open method, lock the door, probe MMC profile, and reject writes unless writable media and capabilities permit them. Release decrements use count, flushes/finalizes DVD+RW or MRW state on last close, unlocks the door unless kept locked, calls the low-level release method, and optionally auto-ejects. `cdrom_ioctl()` first handles uniform ioctls, then tries MMC packet-command implementations, then falls back to low-level audio ioctls.

### State And Persistence
Global state includes module parameters/sysctl defaults, `cdrom_list`, and `cdrom_mutex`. Per-device state includes options, capability mask, media-change flags for VFS and ioctl consumers, last media-change timestamp, use count, lock state, media-written flag, MMC profile, CDDA read method fallback, and changer slot data. Persistent effects are mostly device-side: tray position, door lock, selected slot, media format/flush/finalize state, and sysctl-visible policy defaults.

### Dependencies And Integration Points
The file depends on block devices/gendisks, low-level optical drivers, SCSI/MMC packet command opcodes, Linux CD-ROM UAPI structures, sysctl/procfs, user-copy helpers, capability checks, media event integration, and optional compat syscall handling. It acts as the compatibility layer between old CD-ROM ioctls and modern packet-command capable drives.

### Risks And Edge Cases
Media-change buffering is explicitly racy: `vfs_events` and `ioctl_events` are updated without exclusion around low-level `check_events()`. Many ioctl paths depend on user-provided structures and must preserve copy bounds and format conversion between MSF and LBA. Writable-media checks vary by MRW, DVD-RAM, DVD+RW, MO, and random writable features, and conservative failures may expose read-only behavior. Some reads still have FIXME comments for upper-bound checking. CDDA fallback mutates the per-device read method after errors. Door locking and `use_count` policy must avoid ejecting or unlocking while other opens remain. Sysctl info uses a fixed 1000-byte buffer and can truncate on many drives.

### Test Signals
High-value tests include register/unregister with incomplete ops, open with tray open/no media/audio-only/data/mixed media, nonblocking ioctl-only open, write opens across MRW/DVD-RAM/DVD+RW/MO media, release finalization and auto-eject, media-change ioctls and timestamps, changer slot selection, DVD auth/read-structure paths, CDDA reads with fallback, compat `CDROMREADAUDIO` and `CDROM_LAST_WRITTEN`, sysctl reads/writes, and fuzzing ioctl user-copy boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cdrom/cdrom.c -->
