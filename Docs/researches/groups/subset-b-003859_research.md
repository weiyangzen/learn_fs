# subset-b-003859 Research

This grouped report covers I2C mux drivers and the I3C core/master controller files listed in work item `subset-b-003859`. Each section is bounded by the required source-path markers for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca954x.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca954x.c

Purpose: Implements the Linux I2C mux driver for NXP PCA954x/PCA984x and compatible Maxim MAX735x/MAX736x switches. It exposes each downstream channel as an `i2c_adapter`, drives the mux register through the parent bus, supports regulator/reset resources, optional nested IRQ domains for interrupt-capable parts, sysfs idle-state control, and resume-time reinitialization.

Important APIs, types, and functions: `enum pca_type`, `struct chip_desc`, and `chips[]` encode per-device channel count, mux-vs-switch semantics, enable bit, IRQ capability, and optional I2C device ID validation. `struct pca954x` persists chip description, `last_chan`, `idle_state`, client, IRQ domain, supply, and reset handles. `pca954x_reg_write()` uses `__i2c_smbus_xfer()` to avoid recursively locking the mux parent. `pca954x_regval()`, `pca954x_select_chan()`, and `pca954x_deselect_mux()` implement channel state transitions. `idle_state_show/store()` provides runtime idle policy changes. `pca954x_irq_setup()` and `pca954x_irq_handler()` expose downstream interrupt lines as nested IRQs. `pca954x_probe()`, `pca954x_remove()`, and `pca954x_resume()` own lifecycle.

Control flow: Probe checks SMBus byte capability, allocates an `i2c_mux_core` for up to 8 channels, enables `vdd`, deasserts reset through reset-controller or legacy GPIO, chooses chip data from OF or ID table, optionally validates PCA984x identity through `i2c_get_device_id()`, reads `idle-state` or `i2c-mux-idle-disconnect`, writes the initial register value with `pca954x_init()`, creates nested IRQ mappings if supported, adds one adapter per channel, requests the shared threaded IRQ, and finally publishes `idle_state`. Normal transfers enter through the I2C mux framework, which calls `pca954x_select_chan()` before accessing a child adapter and `pca954x_deselect_mux()` afterward. Resume repeats `pca954x_init()` to restore hardware state.

State and persistence: Hardware-visible state is the single mux register and optional MAX7357 configuration register. Software caches `last_chan` to suppress redundant writes and `idle_state` with `READ_ONCE/WRITE_ONCE` because sysfs may change it concurrently with mux activity. IRQ domain mappings live until cleanup. Regulator enable is balanced in `pca954x_cleanup()`, but reset is only deasserted during probe.

Dependencies and integration points: Depends on I2C core, `i2c-mux`, SMBus byte operations, firmware properties, regulator, reset, GPIO descriptor, IRQ domain, and PM sleep callbacks. It integrates with OF compatible tables, legacy I2C ID matching, Linux device attributes, nested IRQ handling, and the mux framework adapter creation/removal path.

Risks: Recursive bus locking is avoided by direct `__i2c_smbus_xfer()`, so regressions here can deadlock under mux transfers. `last_chan` must stay consistent after failed writes and resume. IRQ support assumes interrupt status bits start at `PCA954X_IRQ_OFFSET` and only level-low child IRQs are valid. Cleanup disables the regulator before deleting adapters, which is existing behavior but means users must not access child adapters after removal begins. MAX7357 enhanced-mode writes require byte-data functionality; otherwise features silently degrade with a warning.

Test signals: Probe with each supported compatible should create the expected number of child adapters and log mux vs switch. Exercise `idle_state` with `MUX_IDLE_AS_IS`, `MUX_IDLE_DISCONNECT`, and valid channel values while transfers are active. Suspend/resume should restore selected/disconnected state. IRQ-capable parts should route child interrupts and reject non-level-low IRQ type configuration. Negative tests include missing regulator, bad device ID, unsupported SMBus byte, invalid idle value, and failed child adapter creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca954x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pinctrl.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pinctrl.c

Purpose: Implements a platform I2C mux whose channels are selected by pinctrl states instead of a discrete mux register. It is intended for boards where different I2C bus paths are selected by changing pin ownership or muxing through the pinctrl subsystem.

Important APIs, types, and functions: `struct i2c_mux_pinctrl` holds a `struct pinctrl *` and a flexible array of `struct pinctrl_state *`. `i2c_mux_pinctrl_select()` applies the state for a channel. `i2c_mux_pinctrl_deselect()` applies the final `"idle"` state when present. `i2c_mux_pinctrl_root_adapter()` inspects each pinctrl setting and ensures all involved pin controllers map to the same I2C root adapter. `i2c_mux_pinctrl_parent_adapter()` resolves the `i2c-parent` phandle. Probe and remove wire the platform driver to `i2c_mux_alloc()`, `i2c_mux_add_adapter()`, and `i2c_mux_del_adapters()`.

Control flow: Probe counts `pinctrl-names`, resolves the parent I2C adapter, allocates mux private storage sized for all states, obtains pinctrl, looks up each named state, treats a last state named `"idle"` as a deselect state, detects whether the mux can be `mux_locked`, and adds adapters for all non-idle states. Selection is a direct call to `pinctrl_select_state()`. Removal deletes child adapters and releases the parent adapter reference.

State and persistence: The driver persists only pinctrl state pointers and the mux core. It does not cache a current channel or store hardware-specific configuration. The active state is owned by the pinctrl provider and remains selected until another channel or idle state is selected.

Dependencies and integration points: Depends on OF, pinctrl consumer APIs, internal pinctrl core structures for settings traversal, I2C adapter lookup by node, and I2C mux core. Device-tree properties `i2c-parent` and `pinctrl-names` are mandatory, and `"idle"` has special ordering semantics.

Risks: The driver includes `../../pinctrl/core.h` and walks pinctrl internals, so pinctrl core layout changes can break it. The `"idle"` state must be last or probe fails. `mux_locked` inference requires all state settings to share the same root adapter; an incorrect result affects mux-core locking behavior. Missing parent adapter causes probe deferral.

Test signals: Valid DT should create one child adapter per non-idle pinctrl state. A non-last `"idle"` state should fail probe with `-EINVAL`. Platforms with states rooted in different I2C adapters should run with `mux_locked = false`; same-root states should log `mux-locked i2c mux`. Transfer tests should verify state changes and idle deselect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pinctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-reg.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-reg.c

Purpose: Provides an I2C mux implementation controlled by writing channel values to a memory-mapped register. It supports platform data and device-tree configuration, register sizes of 1, 2, or 4 bytes, endian selection, optional posted-write readback, and optional idle-state deselection.

Important APIs, types, and functions: `struct regmux` wraps `struct i2c_mux_reg_platform_data`. `i2c_mux_reg_set()` performs endian-aware `iowrite8/16/32` and optional readback. `i2c_mux_reg_select()` and `i2c_mux_reg_deselect()` are mux-core callbacks. `i2c_mux_reg_probe_dt()` parses `i2c-parent`, child `reg` channel values, endianness, `write-only`, optional `idle-state`, and MMIO resource. `i2c_mux_reg_probe()` allocates data, falls back to platform resources, validates register size, allocates mux core, and adds adapters.

Control flow: Probe builds `mux->data` from platform data or DT, obtains the parent adapter by numeric adapter ID, maps the register if not supplied, validates `reg_size`, allocates an `i2c_mux_core`, sets `muxc->deselect` if idle is configured, and adds one child adapter per value. Selecting a channel writes the child channel ID supplied to `i2c_mux_add_adapter()`, which is the DT child `reg` value or platform value. Deselect writes `idle` only when `idle_in_use` is true.

State and persistence: Persistent software state is static platform/DT-derived data: parent adapter id, value array, base adapter numbering, mapped register, register size, endianness, write-only flag, and idle value. Hardware state is the mux register. There is no last-value cache, so each selection writes.

Dependencies and integration points: Uses OF address/resource parsing, `of_find_i2c_adapter_by_node()`, platform data ABI in `linux/platform_data/i2c-mux-reg.h`, devm MMIO mapping, and I2C mux core. The driver binds to `compatible = "i2c-mux-reg"` or platform driver name.

Risks: DT parsing uses child `reg` without checking read errors, so malformed children can produce zero values. Default endianness is compile-time host endian when neither `little-endian` nor `big-endian` is specified; this must match hardware. Readback is skipped for `write-only`, but otherwise uses same-size reads only to flush posted writes. Invalid register size fails probe.

Test signals: Validate 8/16/32-bit register writes with both endian modes, posted write flushing on non-write-only mappings, idle deselect behavior, and base adapter numbering. Probe deferral should occur until the parent adapter exists. Fault tests should cover missing `i2c-parent`, invalid resource size, and adapter-add rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/i3c/Kconfig

Purpose: Defines top-level kernel configuration for the I3C subsystem and a helper dependency symbol for drivers that can bind over either I2C or I3C.

Important APIs, types, and functions: `menuconfig I3C` is a tristate that selects `I2C` and enables the I3C core module named `i3c`. It sources `drivers/i3c/master/Kconfig` only when I3C is enabled. `config I3C_OR_I2C` is a tristate dependency helper for dual-protocol client drivers using `module_i3c_i2c_driver()`.

Control flow: Kconfig exposes the I3C menu, conditionally includes master-controller options, and sets `I3C_OR_I2C` to module when I3C is modular or to the I2C state otherwise. There is no runtime control flow.

State and persistence: Configuration persists in kernel build artifacts and controls whether `device.o`, `master.o`, and selected master drivers are built in or as modules.

Dependencies and integration points: Integrates with kernel Kconfig, the I2C subsystem, I3C master driver Kconfig, and client-driver dependency expressions.

Risks: Incorrect dependency use by dual I2C/I3C drivers can produce impossible built-in/module combinations when `CONFIG_I3C=m`. The top-level `select I2C` couples I3C availability to I2C core build behavior.

Test signals: Build matrix should cover `I3C=n`, `I3C=m`, and `I3C=y`; dual client drivers using `depends on I2C_OR_I3C` should compile in valid combinations and be rejected in invalid built-in-over-module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/Makefile -->
# sources/distributed-fs/ceph-client/drivers/i3c/Makefile

Purpose: Builds the I3C core object and descends into the master-controller directory.

Important APIs, types, and functions: `i3c-y := device.o master.o` links the public device API and core master/bus implementation into `i3c.o`. `obj-$(CONFIG_I3C) += i3c.o` and `obj-$(CONFIG_I3C) += master/` are the only build rules.

Control flow: Kbuild includes these objects when `CONFIG_I3C` is enabled. Runtime behavior is determined by the compiled source files.

State and persistence: Build output persists as built-in objects or `i3c.ko` depending on `CONFIG_I3C`.

Dependencies and integration points: Integrates with the Kbuild object aggregation model and with `drivers/i3c/master/Makefile`.

Risks: Adding new core files requires updating `i3c-y`; adding master drivers belongs in the subdirectory Makefile. A missing object here can expose unresolved symbols for exported I3C APIs.

Test signals: `make drivers/i3c/` should build `device.o`, `master.o`, and selected master subdir objects for modular and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/device.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/device.c

Purpose: Exposes the public I3C device-driver API. It validates client requests, applies runtime PM and bus locking, delegates to locked core helpers in `master.c`, provides IBI lifecycle wrappers, supports device information and ID-table matching, and registers/unregisters `struct i3c_driver` instances with the I3C bus type.

Important APIs, types, and functions: Exported functions include `i3c_device_do_xfers()`, `i3c_device_do_setdasa()`, `i3c_device_get_info()`, `i3c_device_request_ibi()`, `i3c_device_enable_ibi()`, `i3c_device_disable_ibi()`, `i3c_device_free_ibi()`, `i3cdev_to_dev()`, `i3c_device_match_id()`, `i3c_device_get_supported_xfer_mode()`, `i3c_driver_register_with_owner()`, and `i3c_driver_unregister()`. It depends on internal helpers such as `i3c_bus_rpm_get()`, `i3c_bus_normaluse_lock()`, and `i3c_dev_*_locked()`.

Control flow: Transfer and SETDASA APIs acquire runtime PM, take the bus normal-use read lock, call the corresponding locked helper, unlock, and release PM. IBI request validates handler and slot count, then locks the bus and the device IBI mutex before delegating allocation to the master. Enable and disable manage runtime PM differently because enabled IBIs may need the controller awake unless `rpm_ibi_allowed` permits autosuspend. Matching reads device info and compares DCR, manufacturer, part, and extra-info fields while respecting random-PID rules.

State and persistence: This file does not own persistent structures beyond driver registration metadata. It observes `dev->desc`, `dev->desc->info`, `dev->desc->ibi`, and bus PM policy. IBI enable may intentionally hold a runtime PM reference until disabled when IBI wake is not allowed under runtime suspend.

Dependencies and integration points: Integrates public client drivers with the I3C core bus type from `master.c`, runtime PM, mutex and rwsem locking, I3C ID tables, and master-controller operation implementations.

Risks: Callers must supply non-empty transfer buffers; invalid `data.in` for either direction is rejected because the union field aliases storage. IBI PM reference balancing is subtle: enable keeps PM active on success unless runtime IBI is allowed, while disable drops PM on success or when runtime IBI is allowed. `i3c_device_get_supported_xfer_mode()` assumes a valid descriptor and master. Freeing IBI resources while enabled is guarded in the locked helper but should still be avoided by client drivers.

Test signals: Unit-style driver tests should verify invalid transfer arrays, zero transfer count, ID matching with random PID, IBI request without handler or slots, enable/disable PM balance, and driver registration without a probe returning `-EINVAL`. Integration tests need a master driver to confirm exported APIs reach controller ops under the right locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/internals.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/internals.h

Purpose: Declares private interfaces shared between the I3C public device API and the core master implementation, and provides endian-safe 32-bit FIFO helpers for controller drivers.

Important APIs, types, and functions: Declares runtime PM helpers `i3c_bus_rpm_get/put()` and `i3c_bus_rpm_ibi_allowed()`, bus locking helpers `i3c_bus_normaluse_lock/unlock()`, locked device operations `i3c_dev_setdasa_locked()`, `i3c_dev_do_xfers_locked()`, IBI helpers, and inline FIFO helpers `i3c_writel_fifo()` and `i3c_readl_fifo()`.

Control flow: FIFO writes call `writesl()` for full words and write one zero-padded tail word for remaining bytes. FIFO reads call `readsl()` for full words and read one tail word into a temporary before copying remaining bytes. The declared functions are implemented primarily in `master.c` and called by `device.c` and controller drivers.

State and persistence: No persistent state is defined here. FIFO helpers affect device FIFO MMIO state and preserve byte order on big-endian targets by using string I/O helpers rather than scalar `readl/writel` for tail words.

Dependencies and integration points: Depends on `linux/i3c/master.h` and `linux/io.h`. Used by ADI, Cadence, and DesignWare master drivers for RX/TX/IBI FIFOs and by `device.c` for private core calls.

Risks: The helpers use `buf + offset` on `void *`, relying on GNU C extensions accepted by the kernel. Passing a buffer shorter than `nbytes` or a FIFO that cannot tolerate tail word accesses is unsafe. Declarations are private; exporting them broadly would undermine bus-lock invariants.

Test signals: FIFO helper tests are hardware-facing: verify non-multiple-of-four transfer lengths on little and big endian systems, ensure tail bytes are preserved, and check that controller drivers do not overrun buffers when hardware reports short reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master.c

Purpose: Implements the I3C core bus and master-controller framework. It owns the `i3c_bus_type`, bus ID allocation, device sysfs attributes and modaliases, address-slot management, CCC helpers, dynamic address assignment orchestration, I2C compatibility adapter, IBI dispatch and generic IBI pools, master registration/unregistration, and private locked operations used by `device.c`.

Important APIs, types, and functions: Global state includes `i3c_bus_idr`, `i3c_core_lock`, `__i3c_first_dynamic_bus_num`, and `i3c_bus_notifier`. Exported APIs include `i3c_bus_type`, bus iterator/notifier registration, hotjoin enable/disable, free-address lookup, `i3c_master_entdaa_locked()`, `i3c_master_enec_locked()`, `i3c_master_disec_locked()`, `i3c_master_defslvs_locked()`, `i3c_master_do_daa_ext()`, `i3c_master_do_daa()`, DMA map/unmap helpers, `i3c_master_set_info()`, `i3c_master_add_i3c_dev_locked()`, IBI queue/generic pool helpers, and `i3c_master_register/unregister()`. Internal helpers manage address slots, OF boardinfo parsing, I2C adapter operations, and device attach/detach.

Control flow: `i3c_init()` registers an I2C bus notifier and the I3C bus type. `i3c_master_register()` validates controller ops, initializes the master device and bus, parses firmware child nodes, determines mixed/pure bus mode from I2C LVR data, allocates a workqueue, runs `i3c_master_bus_init()`, registers the master device, creates an I2C adapter facade, notifies listeners, enables runtime PM for the I3C master device, marks initialization done, and registers discovered I3C devices. Bus initialization attaches static I2C devices, calls controller `bus_init`, requires `i3c_master_set_info()`, optionally slows speed for RSTDAA, disables events, reserves requested dynamic addresses, optionally SETDASA-attaches static I3C devices, and performs DAA. DAA delegates actual bus transactions to controller `do_daa()`, then registers new devices. I2C transfers on the compatibility adapter locate an `i2c_dev_desc` and call controller `i2c_xfers`. IBI hardware events are queued by controller drivers through `i3c_master_queue_ibi()` and executed in a per-device ordered workqueue.

State and persistence: `struct i3c_bus` tracks id, mode, SCL rates, current master, address-slot bitmap, and I2C/I3C device lists. `struct i3c_master_controller` owns device lists, boardinfo lists, runtime PM flags, workqueue, I2C adapter, and controller ops. Address-slot state reserves forbidden addresses, static I2C addresses, I3C static/dynamic addresses, and desired dynamic addresses. Device descriptors persist retrieved PID/BCR/DCR/HDR/data-speed data plus optional boardinfo, client device, master private data, and IBI state. Generic IBI pools persist preallocated slots and payload buffers.

Dependencies and integration points: Depends on Linux driver core, OF, I2C core and bus notifier, runtime PM, DMA mapping, workqueues, IDR, rwsem locking, and controller-specific `i3c_master_controller_ops`. It is the integration point between client drivers, I2C compatibility clients, firmware-described devices, and hardware master drivers.

Risks: Locking correctness is central: maintenance operations take the bus write lock, normal transfers take the read lock, and controller drivers still need queue locks to serialize hardware. Address-slot bookkeeping must be balanced on every attach, reattach, duplicate hotjoin, and error path. Runtime PM handling spans core and controller drivers. IBI teardown waits for pending work and can try to disable still-enabled IBI resources, so missing controller `disable_ibi` behavior can deadlock or leak. `i3c_device_uevent()` has an uninitialized local if `i3cdev->desc` is NULL, although normal registered-device lifetime should keep descriptors valid. Dynamic address restoration after hotjoin attempts to preserve old/requested addresses and IBI setup, which is complex and error-prone.

Test signals: Build and runtime tests should cover master registration/unregistration rollback, OF parsing for I2C and I3C child nodes, mixed bus mode selection, RSTDAA plus DAA, duplicate device rediscovery with IBI restoration, I2C adapter attach/detach notifier behavior, sysfs attributes, hotjoin sysfs and exported APIs, generic IBI pool exhaustion/recycle, DMA bounce mapping for vmalloc buffers, and runtime PM get/put paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/Kconfig

Purpose: Defines build-time options for supported I3C master controller drivers.

Important APIs, types, and functions: Options include `ADI_I3C_MASTER`, `CDNS_I3C_MASTER`, `DW_I3C_MASTER`, `AST2600_I3C_MASTER`, `SVC_I3C_MASTER`, `MIPI_I3C_HCI`, `MIPI_I3C_HCI_PCI`, and `RENESAS_I3C`. Dependencies gate MMIO support, unsupported architectures for string I/O, Aspeed architecture, PCI, and MFD support.

Control flow: Kconfig presents selectable tristate drivers under top-level `I3C`. Some options select helper subsystems, such as `AST2600_I3C_MASTER` selecting `MFD_SYSCON` and HCI PCI selecting `MFD_CORE`.

State and persistence: Configuration determines which controller modules are compiled and whether they are built-in or loadable modules.

Dependencies and integration points: Integrates master-controller source files with architecture, PCI, MFD, and compile-test configuration. The AST2600 option depends on the DesignWare driver because it wraps the DW common implementation.

Risks: The DesignWare and Cadence/Silvaco exclusions for ALPHA/PARISC reflect reliance on `{read,write}sl()`; relaxing them requires endian/string I/O validation. `AST2600_I3C_MASTER` cannot be enabled without `DW_I3C_MASTER`.

Test signals: Kconfig build matrix should verify dependency visibility and module names. `COMPILE_TEST` coverage should include non-native platforms where dependencies permit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/Makefile -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/Makefile

Purpose: Maps I3C master-controller Kconfig symbols to driver objects and subdirectories.

Important APIs, types, and functions: Builds ADI, Cadence, DesignWare, AST2600, Silvaco, MIPI HCI, and Renesas controller drivers through `obj-$(CONFIG_...)` rules. The HCI driver is delegated to the `mipi-i3c-hci/` subdirectory.

Control flow: Kbuild includes only selected controller objects. There is no runtime control flow in this file.

State and persistence: The selected objects persist in the kernel image or as modules, matching each driver's module name.

Dependencies and integration points: Integrates with `drivers/i3c/master/Kconfig` and controller source files. The AST2600 object links against exported DesignWare common symbols at module or built-in link time.

Risks: Missing Makefile entries lead to selectable but unbuilt drivers. Adding a wrapper driver around common code requires ensuring the common symbols are exported and selected dependencies are correct.

Test signals: `make drivers/i3c/master/` under all master-controller configs should produce the expected object files and descend into HCI only when `CONFIG_MIPI_I3C_HCI` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/adi-i3c-master.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/adi-i3c-master.c

Purpose: Implements the Analog Devices AXI I3C master controller driver. It adapts ADI command, response, data, DAA, IBI, and device-character registers to the core `i3c_master_controller_ops` interface.

Important APIs, types, and functions: `struct adi_i3c_master` owns the I3C core base, free retaining-register slots, IBI slot table, transfer queue, MMIO base, clock, SCL limit, and DAA address staging. `struct adi_i3c_xfer/cmd` describe queued hardware commands. Key functions include FIFO helpers, `adi_i3c_master_supports_ccc_cmd()`, queue start/end/unqueue helpers, `adi_i3c_master_send_ccc_cmd()`, `adi_i3c_master_i3c_xfers()`, attach/reattach/detach for I3C and I2C devices, `adi_i3c_master_do_daa()`, IRQ handlers for command completion, IBI, and DAA address requests, IBI request/enable/disable/free/recycle, and probe/remove.

Control flow: Probe maps registers, enables all clocks, validates AXI peripheral major version 1, disables the core and IRQ mask, requests IRQ, initializes retaining-register and IBI slot state, enables command-response IRQs, and registers with the I3C core. Transfers allocate an `adi_i3c_xfer`, preload TX FIFO, push command FIFO entries, wait for IRQ-driven completion, and reset/unqueue on timeout. DAA precomputes free addresses, enables DAA interrupt handling, sends ENTDAA through the core helper, services target address requests in IRQ by reading PID/BCR/DCR bytes and writing the assigned address, then adds discovered devices and syncs device-character metadata.

State and persistence: Software state includes `free_rr_slots`, per-device master data (`id`, `ibi`, `ibi_pool`), `ibi.slots[]`, the current/queued transfer list, and staged DAA addresses/index. Hardware state includes `REG_DEV_CHAR`, command/data FIFOs, IRQ masks, `REG_IBI_CONFIG`, and speed grade in `REG_OPS`.

Dependencies and integration points: Depends on ADI AXI version registers, clocks, MMIO, IRQs, core FIFO helpers from `internals.h`, and generic IBI pools from `master.c`. It registers as `compatible = "adi,i3c-master-v1"`.

Risks: Probe logs unsupported peripheral version with `dev_err_probe()` but does not return immediately from that call in the visible code path, so version rejection should be reviewed. DAA staging assumes up to `ADI_MAX_DEVS` and increments `daa.index` in IRQ context. IBI handler uses one MDB byte when indicated by BCR and does not copy variable payload data beyond MDB. Transfer command FIFO room can limit how many commands are submitted initially; completion depends on later IRQ behavior. Free RR slot initialization uses `GENMASK(ADI_MAX_DEVS, 1)`, making slot 0 reserved.

Test signals: Hardware or emulation tests should cover CCC get/set error mapping, private SDR transfers with repeated-start flag, I2C transfers rejecting 10-bit addresses, DAA with multiple devices, IBI enable/disable across multiple devices, IBI slot exhaustion, IRQ mask restoration after DAA, and remove-time IRQ/core shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/adi-i3c-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/ast2600-i3c-master.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/ast2600-i3c-master.c

Purpose: Provides ASPEED AST2600 platform-specific glue around the shared DesignWare I3C master implementation. It configures AST2600 global registers, SDA pull-up strength, instance ID, and an IBI PEC workaround.

Important APIs, types, and functions: `struct ast2600_i3c` embeds `struct dw_i3c_master` and adds a syscon regmap, global register index, and SDA pull-up value. `ast2600_i3c_pullup_to_reg()` validates/encodes supported pull-ups. `ast2600_i3c_init()` writes global REG0 and REG1 before bus traffic. `ast2600_i3c_set_dat_ibi()` modifies DesignWare DAT entries to enable IBI PEC when needed. Probe parses `aspeed,global-regs` and `sda-pullup-ohms`, assigns platform ops, and calls `dw_i3c_common_probe()`.

Control flow: Probe allocates wrapper state, obtains a syscon phandle with one argument for controller index, reads/validates pull-up strength with a default of 2000 ohms, installs platform ops, and delegates the rest to the DesignWare common probe. During DW bus init, `ast2600_i3c_init()` writes pull-up and instance configuration. During DW IBI enable/disable, `ast2600_i3c_set_dat_ibi()` may set `DEV_ADDR_TABLE_IBI_PEC`.

State and persistence: AST-specific state is the global regmap/index and configured pull-up. Hardware global registers persist the pull-up and instance ID until reset. The DAT PEC bit persists per IBI-enabled device entry while active.

Dependencies and integration points: Depends on MFD syscon, regmap, OF, platform devices, and `dw-i3c-master.h`. It binds to `aspeed,ast2600-i3c` and requires the shared DW common probe/remove exports.

Risks: Only 2000, 750, and 545 ohm values are accepted. The IBI PEC workaround intentionally truncates one payload byte for affected payload IBIs and warns once. Missing or malformed `aspeed,global-regs` prevents probe.

Test signals: DT tests should validate required syscon phandle and pull-up values. Runtime tests should confirm global register writes, DW registration, IBI payload behavior with PEC enabled, and clean common remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/ast2600-i3c-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.c

Purpose: Implements the Synopsys DesignWare MIPI I3C master driver and exports common probe/remove helpers for platform wrappers such as AST2600. It handles hardware queues, DAT management, timing configuration, DAA, CCC/private/I2C transfers, IBI and hotjoin handling, runtime PM, clock/reset restore, and platform quirks.

Important APIs, types, and functions: `struct dw_i3c_master` is declared in the header and used with private `struct dw_i3c_cmd`, `struct dw_i3c_xfer`, and per-device `struct dw_i3c_i2c_dev_data`. `dw_mipi_i3c_ops` supplies core ops: bus init/cleanup, attach/reattach/detach, DAA, CCC, I3C/I2C transfers, IBI ops, hotjoin ops, and `set_dev_nack_retry`. Exported `dw_i3c_common_probe()` and `dw_i3c_common_remove()` support reuse. PM helpers restore timing and DAT state after runtime suspend.

Control flow: Common probe maps MMIO, enables clocks, deasserts optional reset, initializes queues and locks, requests IRQ, enables runtime PM, reads FIFO and DAT capacities, applies OF/ACPI quirks, initializes hotjoin work, and registers the master. Bus init runs platform `init`, configures I2C/I3C timing for pure or mixed mode, assigns the master dynamic address, calls `i3c_master_set_info()`, configures interrupts and rejects all IBIs by default, then enables the controller. Transfers allocate a `dw_i3c_xfer`, check FIFO depth, preload TX FIFO, program command queue entries, wait for IRQ completion, and reset queues on error or timeout. DAA preprograms free DAT entries with candidate dynamic addresses, issues ENTDAA hardware command, and adds newly assigned devices. IRQ completion drains responses, maps hardware errors to Linux errors, starts the next queued transfer, and handles IBI threshold events.

State and persistence: Software state includes FIFO depths, DAT start/maxdevs, `free_pos`, per-DAT address metadata, `sir_rej_mask`, timing register snapshots, PM quirk flags, and transfer queue. Hardware state includes DEVICE_CTRL, DEVICE_ADDR, DAT entries, queue/FIFO state, timing registers, interrupt masks, and IBI reject masks. Runtime resume reconstructs timing, dynamic/static addresses, interrupts, and controller enablement.

Dependencies and integration points: Depends on `internals.h` FIFO helpers, I3C master core ops, runtime PM, clk/reset/pinctrl, OF and ACPI match data, platform IRQ/MMIO, and optional platform ops from wrappers. ACPI `AMDI0015` applies AMD timing, while OF `altr,agilex5-dw-i3c-master` disables runtime PM.

Risks: Queue error paths reset FIFOs and resume the controller; incomplete reset polling could leave hardware stuck. DAA calculations rely on `cmd->rx_len` to infer new devices. IBI SIR rejection uses a 32-bit hash-like bit index derived from dynamic address, so collisions are possible by design and must match hardware semantics. Hotjoin enable holds a runtime PM reference until disabled. Platform `set_dat_ibi` runs under `devs_lock` and must not sleep. Timeout and runtime PM interactions are a high-risk area.

Test signals: Exercise pure and mixed bus timing, ACPI/OF quirks, runtime suspend/resume with active DAT entries, CCC get/set including unsupported ENTDAA through CCC path, private I3C and I2C transfers over FIFO depth limits, DAA discovery, hotjoin-triggered DAA, IBI payload reception and slot exhaustion, `dev_nack_retry_count` sysfs, shutdown interrupt masking, and wrapper-driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.h -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.h

Purpose: Defines the shared DesignWare I3C master data structures and platform hook contract used by the base DW driver and platform-specific wrappers.

Important APIs, types, and functions: `DW_I3C_MAX_DEVS` caps the software DAT mirror at 32 entries. `struct dw_i3c_master_caps` stores command/data FIFO depths. `struct dw_i3c_dat_entry` mirrors address, I2C-vs-I3C flag, and IBI target device per DAT slot. `struct dw_i3c_master` embeds `i3c_master_controller` and stores MMIO, clocks, reset, queue state, timing snapshots, quirk flags, DAT metadata, lock-protected IBI device pointers, platform ops, and hotjoin work. `struct dw_i3c_platform_ops` provides optional `init` and `set_dat_ibi` callbacks. `dw_i3c_common_probe/remove()` are exported for wrappers.

Control flow: The header has no runtime flow, but its callbacks are invoked by `dw-i3c-master.c`: `init()` during early bus init before transactions, and `set_dat_ibi()` while enabling/disabling DAT IBI configuration under the DAT lock.

State and persistence: The structures defined here are the persistent state for a DW controller instance. Timing snapshots support runtime PM restore. `devs_lock` protects changes to `devs[].ibi_dev` against IRQ-time IBI lookup.

Dependencies and integration points: Depends on clocks, reset controls, I3C master core, platform devices, and Linux types. It is included by both the base DW driver and AST2600 wrapper.

Risks: Wrappers embedding `struct dw_i3c_master` must keep it as the member expected by `container_of()` conversions. Platform callbacks must obey locking constraints, especially no sleeping in `set_dat_ibi()`. Increasing hardware device capacity above `DW_I3C_MAX_DEVS` would require array resizing.

Test signals: Compile tests should cover both standalone DW and wrapper builds. Runtime tests should verify platform ops are optional, wrapper `init` failures abort registration, and IBI DAT hooks execute under expected conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/dw-i3c-master.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/i3c-master-cdns.c -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/i3c-master-cdns.c

Purpose: Implements the Cadence I3C master controller driver. It maps Cadence command/response FIFOs, retaining registers, IBI response/data FIFOs, hotjoin work, clock prescalers, and device slots to the core I3C master ops.

Important APIs, types, and functions: `struct cdns_i3c_master` owns core base, capabilities, free retaining-register slots, IBI slots, transfer queue, sysclk, and device data. `struct cdns_i3c_cmd/xfer` represent queued commands. Important routines include FIFO helpers, CCC support filtering, controller enable/disable, transfer queue start/end/unqueue, CCC/I3C/I2C transfer ops, retaining-register attach/reattach/detach for I3C/I2C, DAA, bus init and cleanup, IBI request/enable/disable/free/recycle, IRQ demux, hotjoin work, and probe/remove.

Control flow: Probe validates device ID, maps MMIO, enables `pclk` and `sysclk`, disables interrupts, requests IRQ, reads hardware capability registers, initializes IBI slots and thresholds, clears device slots, and registers with the I3C core. Bus init selects pure/mixed mode, programs I3C and I2C prescalers, prepares RR0 for master slot 0, reads master identity, sets optional HDR DDR capability, programs hotjoin/halts/MCS/data-hold controls, and enables the controller. Transfers write TX FIFO and command FIFO, set master command start, enable command-empty IRQ, then complete when command responses drain. DAA pre-fills inactive retaining registers with candidate addresses, sends ENTDAA, adds devices found active after DAA, clears unused slots, sends DEFSLVS, updates SCL limits, and enables HJ/MR events.

State and persistence: Software tracks hardware capacities, `free_rr_slots`, IBI slot ownership, `i3c_scl_lim`, and queued transfers. Hardware state includes CTRL, PRESCL registers, DEVS_CTRL active bits, DEV_ID retaining registers, SIR_MAP entries, FIFO contents, and interrupt masks. SCL limit updates may disable and re-enable the controller around PRESCL changes.

Dependencies and integration points: Depends on OF compatible `cdns,i3c-master`, `pclk` and `sysclk`, MMIO/IRQ resources, I3C core ops, and generic IBI pools. It advertises support for more CCCs than some controllers, including `DEFSLVS`, `GETACCMST`, and HDR entry forms.

Risks: Several error conditions are converted to broad `-EIO`, `-ENOSPC`, or `-EINVAL`, so higher layers may have limited diagnostics. IBI handling has a FIXME for FIFO overflow reporting. `cnds_i3c_master_demux_ibis` typo is harmless but visible. DAA relies on hardware active-slot bits and proper clearing of unused retaining registers. Prescaler math can return `-ERANGE`; board clock rates and requested SCL rates need validation.

Test signals: Test probe with bad DEV_ID, clock failures, and capability variations. Runtime tests should cover command timeout unqueue and FIFO flush, CCC error mapping, private SDR length limit, I2C 10-bit handling, DAA with hotjoin, SIR_MAP enable/disable rollback, IBI payload truncation to max length, SCL limit update from device max data speeds, and clean hotjoin work cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/i3c-master-cdns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/Makefile

Purpose: Builds the MIPI I3C Host Controller Interface driver and optional PCI glue.

Important APIs, types, and functions: `obj-$(CONFIG_MIPI_I3C_HCI) += mipi-i3c-hci.o` builds the aggregate HCI module from `core.o`, `ext_caps.o`, `pio.o`, `dma.o`, command-version files, DAT/DCT support, and quirks. `obj-$(CONFIG_MIPI_I3C_HCI_PCI) += mipi-i3c-hci-pci.o` builds the PCI transport glue.

Control flow: Kbuild aggregates the listed HCI implementation objects when the HCI config is enabled. Runtime behavior is in those source files, not the Makefile.

State and persistence: Build configuration determines whether `mipi-i3c-hci` and `mipi-i3c-hci-pci` are built as modules or built-in objects.

Dependencies and integration points: Integrates with `drivers/i3c/master/Kconfig` options `MIPI_I3C_HCI` and `MIPI_I3C_HCI_PCI`. The object list shows internal decomposition into core, extended capabilities, PIO, DMA, command formats, DAT/DCT tables, and quirks.

Risks: Adding a new HCI command/table implementation requires updating this aggregate list. PCI support can be built only when the core HCI object is available.

Test signals: Build tests should verify core-only HCI and HCI+PCI configurations, both modular and built-in, and ensure all aggregate objects resolve symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/Makefile -->
