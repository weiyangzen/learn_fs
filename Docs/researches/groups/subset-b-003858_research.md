# subset-b-003858 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-base.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-base.c

Purpose: main Linux I2C core implementation for this tree. It defines the I2C bus type, client and adapter device types, matching and uevent logic, adapter/client registration, class-based probing, transfer dispatch, bus recovery, host-notify IRQ domains, firmware timing parsing, debugfs roots, and DMA-safe message buffer helpers.

Important APIs: exported entry points include `i2c_add_adapter()`, `i2c_add_numbered_adapter()`, `devm_i2c_add_adapter()`, `i2c_del_adapter()`, `i2c_register_driver()`, `i2c_del_driver()`, `i2c_new_client_device()`, dummy/ancillary/scanned client helpers, `i2c_transfer()`, `__i2c_transfer()`, `i2c_recover_bus()`, `i2c_parse_fw_timings()`, adapter lookup helpers, and DMA bounce-buffer helpers. Key state is `core_lock`, `i2c_adapter_idr`, `i2c_bus_type`, `i2c_client_type`, and `i2c_adapter_type`.

Control flow: `postcore_initcall(i2c_init)` registers the bus, debugfs root, dummy driver, and firmware reconfig notifiers. Adapter registration allocates an ID, initializes locks/runtime PM/host-notify IRQs, adds the device, registers OF/ACPI/static clients, and notifies already-registered drivers. Client creation validates address/flags, serializes address reservation, sets fwnode/software node/device name, and calls `device_register()`. Transfers lock the adapter segment, reject suspended adapters and quirk violations, optionally trace messages, retry `-EAGAIN` until timeout, and dispatch to atomic or normal algorithm callbacks.

State and persistence: persistent kernel state includes adapter IDs, adapter/client devices, address locks, user-created clients, debugfs directories, host-notify IRQ domains, devres groups, wake IRQ setup, PM-domain attachment, and firmware-populated flags. Runtime mutable state includes adapter timeout/retries, recovery GPIO/pinctrl setup, suspend-report bits, and tracepoint static key reference counts.

Dependencies and integration: integrates with driver core, OF, ACPI, PM runtime/domains, debugfs, IRQ domains, GPIO/pinctrl recovery, SMBus core, tracepoints, and mux traversal for address-conflict checks. External adapter drivers provide `struct i2c_algorithm`; client drivers bind through `struct i2c_driver`.

Risks: lifecycle ordering is delicate around `device_register()` failures, fwnode reference release, adapter delete waits, and dummy-client two-pass removal. Address collision checks must include mux parents/children. Atomic transfer mode only works when algorithms provide atomic callbacks. Class probing can still instantiate legacy devices and has corruption-avoidance special cases. Recovery and host-notify setup depend on firmware resources.

Test signals: adapter add/delete, OF/ACPI/static client enumeration, sysfs `new_device`/`delete_device`, transfer retry/quirk paths, suspended-transfer warnings, bus recovery with GPIO/pinctrl, host-notify IRQ mapping, class scanning, DMA-safe buffer copyback, debugfs cleanup, and module unload with `DEBUG_KOBJECT_RELEASE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of-prober.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of-prober.c

Purpose: OF component prober for boards that describe multiple possible drop-in I2C components as disabled or `fail-needs-probe`. It powers shared resources, probes candidate addresses, and enables the responding device-tree node with a persistent changeset.

Important APIs: `i2c_of_probe_component()` is the main exported namespace API. Simple helper exports include `i2c_of_probe_simple_enable()`, `i2c_of_probe_simple_cleanup_early()`, `i2c_of_probe_simple_cleanup()`, and `i2c_of_probe_simple_ops`. Important data contracts come from `struct i2c_of_probe_cfg`, `struct i2c_of_probe_ops`, and `struct i2c_of_probe_simple_ctx`.

Control flow: the prober finds the named component type, validates that it is under an available I2C node, no-ops if a candidate is already enabled, obtains the adapter, runs optional enable callbacks, then SMBus-reads each candidate `reg` address. On the first responding device it releases exclusive GPIOs early if requested, updates the node status to `okay`, applies the changeset, runs cleanup, and drops the adapter reference.

State and persistence: successful node enablement is persistent for the running kernel because the `of_changeset` is intentionally leaked after apply. Simple helper state stores optional regulator and GPIO descriptors in the caller-provided context only during probing.

Dependencies and integration: depends on OF dynamic changesets, I2C adapter lookup, SMBus byte reads, regulators, GPIO descriptors, and driver-probe context. It deliberately does not support I2C mux paths yet.

Risks: global node-name assumptions can misidentify unrelated nodes of the same prefix. It assumes non-conflicting addresses and exactly one present component per type. GPIO cleanup ordering matters because the actual client driver may need the same descriptor. A failed or deferred adapter/resource lookup prevents selection.

Test signals: DT overlays with multiple candidates, regulator/GPIO delay options, successful status mutation, no-op reruns after one candidate is enabled, `-EPROBE_DEFER` when the bus is missing, and negative tests for muxed candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of-prober.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of.c

Purpose: device-tree integration for the I2C core. It converts OF child nodes into `i2c_board_info`, instantiates clients when adapters appear, performs OF and sysfs-compatible matching, and handles dynamic OF node add/remove notifications.

Important APIs: `of_i2c_get_board_info()` parses a node into client type, address, flags, fwnode, host-notify, wake, 10-bit, and own-slave settings. `of_i2c_register_devices()` walks adapter children or an `i2c-bus` subnode. `i2c_of_match_device()` combines normal `of_match_device()` with sysfs-created device-name matching. `i2c_of_notifier` handles `CONFIG_OF_DYNAMIC`.

Control flow: adapter registration calls `of_i2c_register_devices()`, which sets `OF_POPULATED`, creates each client through `i2c_new_client_device()`, and clears the flag on failure. Dynamic add finds the parent adapter, marks the new node populated, clears `FWNODE_FLAG_NOT_DEVICE` for fw_devlink, and registers the client. Dynamic remove finds the client by node and unregisters it.

State and persistence: OF node flags record population state; client devices hold fwnode references until unregister. Dynamic status is reflected in kernel device model state, not persistent storage.

Dependencies and integration: depends on OF core, `dt-bindings/i2c/i2c.h` address flags, sysfs name matching, and the core client creation/unregistration APIs.

Risks: malformed `reg` or compatible aliases prevent registration. Duplicate population flags suppress devices. Sysfs compatibility matching is looser than true OF matching and can bind by full compatible or vendor-stripped name. Dynamic remove relies on node-to-client lookup and reference balancing.

Test signals: DT client enumeration, ten-bit and own-slave address flags, `host-notify` and `wakeup-source` properties, overlays adding/removing I2C children, and sysfs-created clients matching OF tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-slave.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-slave.c

Purpose: common I2C slave-mode support. It registers client callbacks with adapters that can act as slave targets, unregisters them, dispatches slave events with tracing, and detects own-slave-address configuration in firmware.

Important APIs: `i2c_slave_register()`, `i2c_slave_unregister()`, `i2c_slave_event()`, and `i2c_detect_slave_mode()` are GPL exports. The adapter algorithm callbacks `reg_slave` and `unreg_slave` are the integration contract, while `client->slave_cb` holds the active callback.

Control flow: registration validates client/callback, warns if the client lacks `I2C_CLIENT_SLAVE`, performs strict 7-bit address validation for non-10-bit clients, checks adapter support, stores the callback, and calls `reg_slave()` under the root adapter lock. Unregister mirrors this through `unreg_slave()` and clears `slave_cb` only on success. Event dispatch calls the callback and emits the slave tracepoint.

State and persistence: the only framework state is `client->slave_cb` plus adapter hardware state established by the adapter driver. Firmware slave-mode detection scans child `reg` properties for `I2C_OWN_SLAVE_ADDRESS`.

Dependencies and integration: used by slave EEPROM/testunit and SMBus host-notify helpers. Depends on trace events, OF/ACPI fwnodes, and adapter algorithm support.

Risks: missing slave flag may collide with normal clients. Adapter callbacks run under root bus lock and must not recurse incorrectly. ACPI slave detection is explicitly unsupported. Callback return values can cause NACK behavior in controller drivers.

Test signals: strict-address rejection, unsupported-adapter `-EOPNOTSUPP`, register/unregister lock coverage, tracepoint output, DT own-slave detection, and client drivers receiving all event types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-smbus.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-smbus.c

Purpose: always-built SMBus helper and emulation layer. It implements exported SMBus read/write convenience APIs, PEC calculation/checking, native SMBus transfer dispatch, I2C-message emulation fallback, block-read emulation, and automatic SMBus Alert client creation hook.

Important APIs: exports include `i2c_smbus_pec()`, byte/byte-data/word/block/I2C-block read-write helpers, `i2c_smbus_xfer()`, `__i2c_smbus_xfer()`, `i2c_smbus_read_i2c_block_data_or_emulated()`, `i2c_new_smbus_alert_device()`, and conditionally `i2c_setup_smbus_alert()`.

Control flow: public helpers fill `union i2c_smbus_data` and call `i2c_smbus_xfer()`. The locked wrapper calls `__i2c_smbus_xfer()`, which rejects invalid block lengths, traces, chooses native normal/atomic SMBus callbacks when available, retries arbitration loss, and falls back to `i2c_smbus_xfer_emulated()` when native support returns `-EOPNOTSUPP`. Emulation builds one or two `i2c_msg` objects, handles special protocols, optional DMA-safe temporary buffers, PEC insertion/checking, and copies replies back to the data union.

State and persistence: no persistent device state except temporary stack/heap message buffers and adapter timeout/retry effects. Alert setup instantiates a client at address `0x0c`.

Dependencies and integration: depends on I2C core transfer locking, trace events, adapter functionality bits, firmware properties for `smbus_alert`, and optional `CONFIG_I2C_SMBUS` module support.

Risks: block length validation, PEC length adjustment, and `I2C_M_RECV_LEN` buffer sizing are error-prone. Emulation only works when adapter I2C transfers support the required flags. Atomic-mode fallback requires atomic master transfers. `I2C_SMBUS_I2C_BLOCK_DATA` intentionally excludes PEC.

Test signals: native and emulated protocol tests, PEC mismatch returns `-EBADMSG`, invalid block-size `-EINVAL`, arbitration retries, tracepoint coverage, DMA temp buffer free paths, and SMBALERT auto-instantiation from IRQ/GPIO properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-smbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core.h

Purpose: private header for I2C framework implementation files. It exposes shared board-info state, internal helpers, firmware integration hooks, SMBus alert setup, and lock/suspend helpers used by core transfer code.

Important APIs/types: `struct i2c_devinfo` stores board-list entries. Externs include `__i2c_board_lock`, `__i2c_board_list`, and `__i2c_first_dynamic_bus_num`. Helpers include `i2c_check_7bit_addr_validity_strict()`, `i2c_dev_irq_from_resources()`, `i2c_in_atomic_xfer_mode()`, `__i2c_lock_bus_helper()`, `__i2c_check_suspended()`, ACPI/OF registration and matching hooks, and `i2c_setup_smbus_alert()`.

Control flow: transfer callers use `__i2c_lock_bus_helper()` to select trylock behavior for late atomic contexts, then `__i2c_check_suspended()` before dispatch. Adapter registration code calls OF/ACPI/SMBus hook declarations that compile to no-ops when features are disabled.

State and persistence: it centralizes access to board registration globals and adapter locked flags. It does not own storage beyond external declarations.

Dependencies and integration: depends on kconfig conditionals, rwsems, system state/preemption, and feature-specific compilation for ACPI, OF, ACPI opregions, and SMBus.

Risks: private helpers define subtle global behavior. Atomic transfer detection is intentionally narrow and may return `-EAGAIN` instead of sleeping. Suspend warnings are rate-limited by a bit flag so repeated bugs can become quiet.

Test signals: all I2C core files build under OF/ACPI/SMBUS enabled and disabled configs, atomic transfer trylock behavior, and suspended adapter rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-dev.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-dev.c

Purpose: character-device frontend exposing adapters as `/dev/i2c-*` for userspace. It registers major `I2C_MAJOR`, creates class devices for adapters, implements read/write and ioctl APIs, and tracks adapter hotplug through bus notifiers.

Important APIs/types: `struct i2c_dev` ties an adapter to a `cdev` and device node. File operations are `i2cdev_read()`, `i2cdev_write()`, `i2cdev_ioctl()`, compat ioctl handling, open, and release. Ioctls cover `I2C_SLAVE`, `I2C_SLAVE_FORCE`, `I2C_TENBIT`, `I2C_PEC`, `I2C_FUNCS`, `I2C_RDWR`, `I2C_SMBUS`, `I2C_RETRIES`, and `I2C_TIMEOUT`.

Control flow: module init reserves device numbers, registers the class and bus notifier, then attaches existing adapters. Opening gets the adapter module reference and allocates an anonymous, unregistered `i2c_client`. Raw read/write require `I2C_FUNC_I2C` and use the current client address. `I2C_RDWR` copies an array of messages and user buffers, enforces count and 8192-byte length limits, handles `I2C_M_RECV_LEN`, marks DMA-safe buffers, transfers, and copies reads back.

State and persistence: `i2c_dev_list` maps minors to adapters under a spinlock. Per-open state is the anonymous client with address, 10-bit, and PEC flags. Ioctls can mutate adapter timeout and retries globally for all users of that adapter.

Dependencies and integration: depends on I2C core adapter lookup, bus notifications, cdev/class APIs, compat ABI translation, uaccess, and SMBus helpers.

Risks: userspace can talk to arbitrary addresses, and `I2C_SLAVE_FORCE` bypasses busy checks. Busy checks deliberately allow unbound registered devices. Adapter timeout/retry mutation is shared state. Message length and receive-length validation are critical for user-copy safety.

Test signals: device-node creation/removal on adapter hotplug, ioctl ABI and compat tests, forced and non-forced address selection, 8192-byte caps, `I2C_M_RECV_LEN` validation, adapter removal while FDs are open, and timeout/retry side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-mux.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-mux.c

Purpose: shared I2C mux framework implementation. It lets mux drivers expose each downstream channel as a child adapter while wrapping transfers with channel select/deselect callbacks and correct parent/root bus locking.

Important APIs: exports `i2c_root_adapter()`, `i2c_mux_alloc()`, `i2c_mux_add_adapter()`, and `i2c_mux_del_adapters()`. Private `struct i2c_mux_priv` stores each child adapter, algorithm, mux core pointer, and channel ID.

Control flow: child transfer callbacks select the channel, call parent `__i2c_transfer()`/`i2c_transfer()` or SMBus equivalents depending on mux locking mode, then deselect if provided. `i2c_mux_alloc()` creates the mux core and stores flags for locked muxes, arbitrators, and gates. `i2c_mux_add_adapter()` builds a per-channel adapter, mirrors parent functionality, timeout, quirks, and firmware node, registers it, and creates sysfs links. Deletion removes links, unregisters adapters, drops OF refs, and frees private data.

State and persistence: mux cores hold parent, callbacks, flags, channel adapter list, and driver-private data. Child adapters persist until explicit deletion. Sysfs links expose mux-to-channel relationships.

Dependencies and integration: depends on the I2C core, OF child-node conventions (`i2c-mux`, `i2c-arb`, `i2c-gate`), ACPI companion preset, and adapter locking APIs.

Risks: lock selection is central to avoiding nested-transfer deadlocks. Channel OF node lookup must support old and new DT layouts. The code assigns atomic callbacks from dynamic algorithm fields, so regressions around `master_xfer`/`xfer` aliases need build coverage. Deselect errors are ignored by transfer wrappers.

Test signals: nested mux topologies, mux-locked and parent-locked transfers, SMBus and I2C functionality inheritance, OF/ACPI channel enumeration, sysfs link creation, and cleanup after partial adapter-add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-eeprom.c

Purpose: I2C slave-mode EEPROM simulator for testing controllers and peer masters. It emulates several 24xx EEPROM sizes and read-only variants, exposes the backing memory through a sysfs binary attribute, and can initialize from firmware.

Important APIs/types: `struct eeprom_data` stores the binary attribute, spinlock, current buffer index, address mask, address-byte count, read-only flag, and flexible backing buffer. The driver binds IDs such as `slave-24c02`, `slave-24c32`, `slave-24c64`, and `slave-24c512` with RO variants.

Control flow: probe decodes size and addressing flags from `driver_data`, allocates backing storage, optionally loads `firmware-name` into the buffer or fills `0xff`, creates `slave-eeprom`, then registers `i2c_slave_eeprom_slave_cb()`. Write events first collect one or two address bytes, then write data when not read-only. Read-request events return the current byte; read-processed increments after the previous byte was accepted. STOP and write-request reset address-byte collection.

State and persistence: EEPROM contents persist in kernel memory for the client lifetime and can be read/written through sysfs. No data survives driver unload or device removal unless reloaded from firmware.

Dependencies and integration: depends on I2C slave core, firmware loader, sysfs binary attributes, bitfield helpers, and spinlocks.

Risks: behavior for incomplete 16-bit addresses is explicitly uncertain. Address wrapping relies on power-of-two sizes. Sysfs writes bypass EEPROM write-protect timing semantics. Callback and sysfs access share a spinlock, but index counters are not themselves locked.

Test signals: slave event sequences, RO write suppression, sysfs binary read/write, firmware preloading, address wraparound, 8-bit vs 16-bit address modes, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-testunit.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-testunit.c

Purpose: programmable I2C slave-mode test target. It accepts register-like command writes from a remote master, delays execution, then performs adapter actions such as reading bytes from another address, emitting SMBus Host Notify, participating in SMBus Alert, block process-call behavior, and returning the kernel version string over repeated-start reads.

Important APIs/types: command enum values include `TU_CMD_READ_BYTES`, `TU_CMD_SMBUS_HOST_NOTIFY`, `TU_CMD_SMBUS_BLOCK_PROC_CALL`, `TU_CMD_GET_VERSION_WITH_REP_START`, and `TU_CMD_SMBUS_ALERT_REQUEST`. `struct testunit_data` stores flags, four command registers, indices, client, delayed work, optional GPIO, and alert completion.

Control flow: the slave callback gathers up to four bytes, validates command numbers, queues delayed work on STOP when a full command is present, NACKs while busy or after errors until STOP, and serves status/version/proc-call bytes on reads. Worker execution performs regular I2C transfers, writes host-notify frames to address `0x08`, or temporarily unregisters/re-registers the client at alert address `0x0c` while asserting a GPIO.

State and persistence: command registers and busy/NACK flags persist until command completion or STOP. Optional GPIO state is used for SMBALERT tests. No persistent storage beyond the device lifetime.

Dependencies and integration: depends on I2C slave core, normal I2C master transfers on the same adapter, workqueues, completions, optional non-sleeping GPIO, and generated `UTS_RELEASE`.

Risks: it intentionally drives complex bus behavior and can conflict with real devices if misconfigured. SMBALERT mode temporarily changes the client address and registration. GPIOs that can sleep are rejected. Workqueue operations after removal are guarded by `cancel_delayed_work_sync()`.

Test signals: scripted command writes, busy/NACK behavior, host-notify delivery, alert completion timeout, repeated-start version reads, delayed execution, and removal during pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-slave-testunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-smbus.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-smbus.c

Purpose: optional SMBus protocol extensions outside the always-built core helpers. It implements SMBALERT handling, a slave-mode SMBus Host Notify receiver helper, and DMI-based SPD EEPROM auto-instantiation helpers.

Important APIs: `i2c_handle_smbus_alert()` schedules alert work for an ARA client. With slave support, `i2c_new_slave_host_notify_device()` and `i2c_free_slave_host_notify_device()` manage a slave client at address `0x08`. DMI exports are `i2c_register_spd_write_disable()` and `i2c_register_spd_write_enable()`.

Control flow: the `smbus_alert` driver binds an alert response address client, obtains an IRQ from setup data, firmware `smbus_alert`, or `smbalert` GPIO, and requests a threaded IRQ. The handler repeatedly reads ARA bytes, decodes alerting address/data bit, invokes the matching client driver's `alert()` callback, and forces all alert handlers if the same unhandled address repeats. Host-notify support collects the first byte of a 3-byte slave write and calls `i2c_handle_smbus_host_notify()`. SPD registration scans DMI memory devices, validates a common memory type, chooses `spd`, `ee1004`, or `spd5118`, and probes addresses `0x50` upward.

State and persistence: alert state stores work item and ARA client. Host-notify state stores received byte index/address in platform data. SPD-instantiated clients persist until adapter removal.

Dependencies and integration: depends on I2C core, SMBus helpers, IRQ/GPIO firmware properties, DMI memory-device data, optional slave core, and client-driver alert callbacks.

Risks: unhandled alerts can loop, mitigated by repeated-address force handling. Host Notify currently ignores the data parameter beyond the notifying address. DMI SPD instantiation is heuristic and skips mixed memory types or unsupported types. DDR5 SPD is skipped when write-disabled mode requests safety.

Test signals: SMBALERT IRQ and polling helper paths, alert callback dispatch, repeated unhandled alert behavior, host-notify slave writes, DMI slot/type combinations, and SPD client creation logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-smbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-stub.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-stub.c

Purpose: software SMBus adapter and chip emulator for testing I2C client drivers without hardware. It creates one virtual adapter and emulates up to ten configured chip addresses with byte, word, I2C-block, and optional SMBus-block register behavior.

Important APIs/types: module parameters include `chip_addr`, `functionality`, `bank_reg`, `bank_mask`, `bank_start`, and `bank_end`. `struct stub_chip` stores the current pointer, 256 word registers, SMBus block list, and optional banked-register storage. The adapter algorithm exposes `stub_xfer()` and `stub_func()`.

Control flow: init validates chip addresses, allocates chip state, initializes SMBus block lists and optional banks, then registers `stub_adapter`. Transfers find the emulated chip by address and implement SMBus command semantics: byte writes update pointer, byte/word data access register storage, I2C block accesses sequential byte registers, and SMBus block writes create/update per-command block buffers. Bank selection changes when the configured bank register is written.

State and persistence: all emulated register and block data live in module memory and reset on module unload. `functionality` is writable and can change advertised capabilities at runtime.

Dependencies and integration: depends on the I2C core adapter registration and SMBus algorithm path. It is typically used with client-driver tests or manual `i2c-dev` transactions.

Risks: no locking protects chip register state, so concurrent users can race. Bank masks assume contiguous bits. SMBus block reads require a prior block write. It does not emulate timing, interrupts, PEC, or real hardware side effects.

Test signals: module load with valid/invalid addresses, client probing on the virtual adapter, byte/word/block command behavior, banked register selection, runtime functionality masking, and cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/Kconfig

Purpose: Kconfig menu for I2C mux, gate, arbitrator, and demux drivers under `drivers/i2c/muxes`. The whole menu depends on `I2C_MUX`.

Important symbols: entries include `I2C_ARB_GPIO_CHALLENGE`, `I2C_MUX_GPIO`, `I2C_MUX_GPMUX`, `I2C_MUX_LTC4306`, `I2C_MUX_PCA9541`, `I2C_MUX_PCA954x`, `I2C_MUX_PINCTRL`, `I2C_MUX_REG`, `I2C_DEMUX_PINCTRL`, `I2C_MUX_MLXCPLD`, and `I2C_MUX_MULE`.

Control flow: build configuration selects which mux drivers compile as built-in or modules. Several symbols enforce subsystem dependencies such as `GPIOLIB`, `OF`, `PINCTRL`, `HAS_IOMEM`, `SENSORS_AMC6821`, `MULTIPLEXER`, and `REGMAP_I2C`.

State and persistence: no runtime state; it controls kernel build state and module availability.

Dependencies and integration: integrates with the I2C mux core and each driver source listed in the corresponding Makefile. Help text documents expected module names.

Risks: dependency mismatches can create build failures or unusable runtime configs. `I2C_MUX_MULE` depends on a specific hwmon sensor driver because the Mule parent function supplies the regmap. `I2C_DEMUX_PINCTRL` selects `OF_DYNAMIC`, reflecting runtime OF changeset requirements.

Test signals: `olddefconfig`, allmodconfig, compile-test combinations for GPIO/OF/PINCTRL/MUX, and verifying module names match Makefile objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/Makefile -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/Makefile

Purpose: object list for I2C mux drivers. It maps each mux Kconfig symbol to its object file and enables debug bus logging flags.

Important entries: object mappings include `i2c-arb-gpio-challenge.o`, `i2c-demux-pinctrl.o`, `i2c-mux-gpio.o`, `i2c-mux-gpmux.o`, `i2c-mux-ltc4306.o`, `i2c-mux-mlxcpld.o`, `i2c-mux-mule.o`, `i2c-mux-pca9541.o`, `i2c-mux-pca954x.o`, `i2c-mux-pinctrl.o`, and `i2c-mux-reg.o`.

Control flow: Kbuild includes objects when the corresponding `CONFIG_` value is `y` or `m`. `ccflags-$(CONFIG_I2C_DEBUG_BUS) := -DDEBUG` enables driver debug prints when configured.

State and persistence: no runtime state.

Dependencies and integration: pairs directly with `Kconfig` and the parent I2C build system.

Risks: a missing object mapping would silently omit a selected driver. Debug flag scope applies to this directory's compilation units.

Test signals: kernel builds for each mux symbol as module and built-in, plus debug config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-arb-gpio-challenge.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-arb-gpio-challenge.c

Purpose: single-channel I2C arbitrator using two GPIO lines in a challenge/response protocol for two masters sharing a bus.

Important APIs/types: `struct i2c_arbitrator_data` stores our claim GPIO, their claim GPIO, slew delay, retry interval, and total wait time. The mux callbacks are `i2c_arbitrator_select()` and `i2c_arbitrator_deselect()`.

Control flow: probe requires OF, allocates an `I2C_MUX_ARBITRATOR` mux core, gets `our-claim` output and one `their-claim` input, rejects more than one peer, reads timing properties, resolves `i2c-parent`, and adds one child adapter. Select asserts our claim, waits for GPIO slew, polls for the other master to deassert, retries by dropping our claim, and times out with `-EBUSY`. Deselect drops our claim and waits slew delay.

State and persistence: runtime state is only GPIO output state and mux adapter lifetime. Timing values persist in driver data.

Dependencies and integration: depends on OF, gpiolib, platform driver core, and `i2c_mux_add_adapter()`.

Risks: only two-master topologies are supported. Timing values directly affect fairness and latency. Busy timeout prevents transfers rather than queuing. GPIO polarity/configuration must match the binding.

Test signals: claim/release GPIO traces, contention with a peer master, timing property defaults, probe defer for missing GPIO/parent, and child adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-arb-gpio-challenge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-demux-pinctrl.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-demux-pinctrl.c

Purpose: pinctrl-based I2C demultiplexer that exposes one logical adapter while switching which physical parent master drives the bus at runtime.

Important APIs/types: `struct i2c_demux_pinctrl_chan` stores parent nodes, active adapter refs, and OF changesets. `struct i2c_demux_pinctrl_priv` stores current channel, bus name, logical adapter, algorithm, and channel array. Sysfs attributes are `available_masters` and writable `current_master`.

Control flow: probe reads at least two `i2c-parent` phandles and `i2c-bus-name`, prepares per-parent changesets marking parents `status = ok`, activates channel 0, and creates sysfs files. Activation applies the changeset, gets the parent adapter, optionally selects the pinctrl state named by `i2c-bus-name`, builds/registers the current logical adapter, and updates `cur_chan`. Changing master deactivates the current adapter, reverts its changeset, drops the parent ref, then activates the requested channel.

State and persistence: active channel, current adapter registration, parent adapter refs, and applied OF changesets persist until channel change or remove.

Dependencies and integration: depends on OF dynamic changesets, pinctrl, platform devices, runtime PM no-callback setup, and I2C core transfer APIs.

Risks: sysfs master switching can disrupt active clients. Failure during changeset or pinctrl selection must revert state correctly. The logical adapter only implements I2C master transfers, not SMBus-specific callbacks. Parent node references and changesets need balanced cleanup.

Test signals: channel switching through sysfs, pinctrl state selection, adapter add/delete on each switch, transfer forwarding to selected parent, invalid channel rejection, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-demux-pinctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpio.c

Purpose: GPIO-controlled I2C multiplexer driver. It maps mux channel IDs to GPIO bit patterns and creates child adapters for each channel.

Important APIs/types: `struct gpiomux` embeds platform data, GPIO count, and descriptor array. Core callbacks are `i2c_mux_gpio_select()` and optional `i2c_mux_gpio_deselect()`. Firmware parsing fills `struct i2c_mux_gpio_platform_data`.

Control flow: probe obtains platform data or parses OF/ACPI firmware for parent adapter, child `reg` values, `idle-state`, and `settle-time-us`. It gets the parent adapter, allocates an I2C mux core, determines whether mux locking is needed by comparing GPIO-controller roots with the I2C root, requests mux GPIOs at the initial idle or first-channel state, and adds one adapter per value. Select writes all GPIOs with `gpiod_set_array_value_cansleep()` and optionally waits; deselect drives the idle state.

State and persistence: GPIO output state represents the selected or idle channel. Mux data stores channel values, parent adapter reference, settle time, and child adapters.

Dependencies and integration: depends on gpiolib, OF/ACPI firmware parsing, platform data compatibility, and I2C mux core.

Risks: incorrect initial state can select an unintended downstream bus during probe. Locking decision depends on root adapter detection for GPIO providers. Firmware child count and `reg` properties must match hardware. No-idle mode leaves last channel selected.

Test signals: GPIO bit patterns for each channel, idle disconnect behavior, settle delay, platform-data and firmware probe paths, mux-locked logging, and partial adapter-add cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpmux.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpmux.c

Purpose: generic-purpose I2C mux using the kernel mux-control subsystem instead of direct GPIO/register control.

Important APIs/types: `struct mux` stores a `struct mux_control *` and a `do_not_deselect` flag. Select/deselect callbacks are `i2c_mux_select()` and `i2c_mux_deselect()`.

Control flow: probe requires OF, gets an unnamed mux control, resolves `i2c-parent`, counts child nodes, allocates a mux core, honors optional `mux-locked`, and for each child validates `reg` against `mux_control_states()` before adding a child adapter. Select calls `mux_control_select()`, recording whether deselect should be skipped after a failed select. Deselect calls `mux_control_deselect()` unless select failed.

State and persistence: selected mux-control state lives in the mux subsystem/hardware. Driver state stores the parent adapter reference, child adapters, and `do_not_deselect` error guard.

Dependencies and integration: depends on OF, mux consumer API, platform driver core, and I2C mux core.

Risks: invalid child `reg` values can exceed mux-control states. Failed select leaves deselect intentionally skipped, so hardware may remain in its previous state. Parent adapter references must be released on all failure paths.

Test signals: child state validation, mux-control select/deselect calls, `mux-locked` behavior, failed select handling, adapter cleanup on bad child nodes, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpmux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-ltc4306.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-ltc4306.c

Purpose: I2C mux/switch driver for Analog Devices/Linear Technology LTC4305 and LTC4306 devices, including optional GPIO support on LTC4306.

Important APIs/types: `enum ltc_type`, `struct chip_desc`, and `struct ltc4306` describe channel count, GPIO count, regmap, and gpiochip. Registers include status, config, mode, and switch. Mux callbacks are `ltc4306_select_mux()` and `ltc4306_deselect_mux()`.

Control flow: probe selects chip data from OF or ID table, checks idle-disconnect property, allocates an `I2C_MUX_LOCKED` mux core, initializes regmap, toggles optional enable GPIO, writes the switch register to verify presence/disconnect channels, configures upstream/downstream accelerators, registers GPIOs if present, and creates adapters for every channel. Select sets the switch mask bit for the chosen channel; deselect clears it when idle disconnect is enabled.

State and persistence: regmap cache and hardware registers hold accelerator, GPIO mode/config, and selected switch state. Child adapters persist until remove. Optional GPIO directions/values are visible through gpiolib.

Dependencies and integration: depends on regmap-I2C, gpiolib, device properties, I2C mux core, and OF/ID matching.

Risks: register bit numbering maps channel to `BIT(7 - chan)`, so channel-count changes need care. Probe uses register writes as presence tests. GPIO mode register is reset to all-inputs during init. Idle disconnect controls whether downstream channels remain connected between transfers.

Test signals: LTC4305 two-channel and LTC4306 four-channel probes, enable GPIO sequencing, accelerator properties, GPIO get/set/direction/config, idle disconnect, and regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-ltc4306.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mlxcpld.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mlxcpld.c

Purpose: Mellanox CPLD-based I2C mux driver using platform data supplied by a parent I2C CPLD client.

Important APIs/types: `struct mlxcpld_mux` stores cached `last_val`, parent I2C client, and `struct mlxcpld_mux_plat_data`. Key callbacks are `mlxcpld_mux_select_chan()` and `mlxcpld_mux_deselect()`.

Control flow: probe requires platform data, chooses SMBus byte-data or raw I2C functionality based on 1-byte or 2-byte register addressing, allocates a mux core, copies platform data, initializes `last_val`, and adds adapters for each platform channel ID. Register writes use `__i2c_smbus_xfer()` for 1-byte register addresses or `__i2c_transfer()` for 2-byte addresses to avoid recursive adapter locking. Select writes the new channel only when it differs from `last_val`; deselect writes zero and clears the cache.

State and persistence: CPLD mux register holds selected channel. `last_val` caches software state to skip redundant writes. Platform data also carries completion notification state for board code.

Dependencies and integration: depends on parent being an I2C client, Mellanox platform data, I2C mux core, and adapter functionality bits.

Risks: platform-data-only design limits firmware self-description. Cached `last_val` can become stale if firmware or another agent changes the CPLD. Register size validation is strict. Completion callback receives adapter pointers after registration and must not outlive them.

Test signals: both register-size modes, functionality rejection, channel cache behavior, deselect writes, completion notification, and partial channel registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mlxcpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mule.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mule.c

Purpose: Theobroma Systems Mule I2C device mux driver. It selects downstream emulated devices by writing a configuration register in the parent Mule MCU regmap.

Important APIs/types: `struct mule_i2c_reg_mux` stores the parent regmap. Constants define config register `0xff` and default device `0`.

Control flow: probe counts child nodes, gets the parent I2C client and regmap, allocates an `I2C_MUX_LOCKED` mux core, writes and reads back the default device to detect older firmware without mux support, registers devm cleanup, then iterates child nodes. Each child `reg` is selected to verify support before a child adapter is added. Unsupported channels on old or limited firmware are warned and skipped. Remove action deletes adapters and returns the mux to default.

State and persistence: selected device is stored in the Mule config register. The driver keeps only the regmap pointer and child adapter registrations. Cleanup always attempts to deselect to default.

Dependencies and integration: depends on parent regmap from the Mule device, OF child nodes, I2C mux core, and platform driver binding `tsd,mule-i2c-mux`.

Risks: old firmware accepts writes but readback stays `0xff`, so only default device can be safely exposed. Per-child selection probes can alter active device during probe. Missing parent regmap blocks operation.

Test signals: readback-based firmware detection, unsupported-child warnings, adapter creation for supported `reg` values, cleanup deselect, and parent regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-mule.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca9541.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca9541.c

Purpose: driver for the NXP PCA9541 two-master I2C bus master selector, modeled as a single-channel arbitrating mux.

Important APIs/types: `struct pca9541` stores client, select timeout, and arbitration timeout. Register helpers `pca9541_reg_read()` and `pca9541_reg_write()` use unlocked SMBus transfers. `pca9541_arbitrate()` implements the datasheet state machine. Mux callbacks are `pca9541_select_chan()` and `pca9541_release_chan()`.

Control flow: probe requires SMBus byte-data support, locks the segment to release any stale bus ownership, allocates an `I2C_MUX_ARBITRATOR` mux core, and adds one child adapter. Select sets an arbitration deadline, loops through `pca9541_arbitrate()`, sleeps/udelay according to short or long retry delay, forces ownership after adapter timeout, and fails after twice the timeout. Release clears bus ownership when this master owns the bus.

State and persistence: hardware control/status registers hold bus ownership, bus-on, bus-init, and test bits. Driver state tracks arbitration timing only during selection.

Dependencies and integration: depends on I2C mux core, SMBus byte-data transfers, jiffies timing, and optional OF match `nxp,pca9541`.

Risks: arbitration forcibly takes ownership after timeout, which can disrupt a peer master. Register access must use unlocked helpers to avoid nested locking. The state-table control array is hardware-specific and fragile. Timeouts inherit adapter timeout settings.

Test signals: two-master contention, forced ownership warning, release behavior, timeout paths, stale-ownership cleanup on probe, and child adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-pca9541.c -->
