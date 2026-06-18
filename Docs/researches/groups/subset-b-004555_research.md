# Research: subset-b-004555

Grouped research for the mlxsw platform, linecard, thermal, hwmon, I2C, PCI, and shared-layout helpers. Each section preserves the source path and is wrapped for reconciliation into the mapped per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_hwmon.c

## Purpose
`core_hwmon.c` exposes Mellanox/NVIDIA mlxsw switch environmental telemetry and fan controls through Linux hwmon sysfs. It builds dynamic hwmon attribute sets for the main board and, when modular systems report active slots, for line cards. It covers ASIC temperature sensors, highest-temperature history/reset, tachometer RPM/faults, PWM duty, module temperatures, module thresholds, module alarm synthesis, and gearbox temperature sensors.

## Important APIs, Types, and Functions
- `struct mlxsw_hwmon_attr` embeds `device_attribute` and tracks the mlxsw hwmon device plus a `type_index` used to map sysfs attributes to ASIC sensor, module, fan, or gearbox indexes.
- `struct mlxsw_hwmon_dev` owns one hwmon registration: attribute arrays, group pointers, sensor counts, slot index, and active state. `struct mlxsw_hwmon` owns the core/bus references and a flexible array of board/line-card devices.
- Sysfs handlers include `mlxsw_hwmon_temp_show()`, `mlxsw_hwmon_temp_max_show()`, `mlxsw_hwmon_temp_rst_store()`, `mlxsw_hwmon_fan_rpm_show()`, `mlxsw_hwmon_fan_fault_show()`, `mlxsw_hwmon_pwm_show()`, `mlxsw_hwmon_pwm_store()`, and module-specific temperature, threshold, label, and alarm handlers.
- `mlxsw_hwmon_temp_init()`, `mlxsw_hwmon_fans_init()`, `mlxsw_hwmon_module_init()`, and `mlxsw_hwmon_gearbox_init()` query mlxsw registers and populate the dynamic sysfs attribute table through `mlxsw_hwmon_attr_add()`.
- Public lifecycle is `mlxsw_hwmon_init()` / `mlxsw_hwmon_fini()`. Line-card integration is through `mlxsw_linecards_event_ops_register()` with `mlxsw_hwmon_got_active()` / `mlxsw_hwmon_got_inactive()`.

## Control Flow
Initialization queries `MGPIR` to size the flexible line-card array, initializes slot 0, adds attributes by querying `MTCAP`, `MFCR`, `MGPIR`, and `MTMP`, registers the main `mlxsw` hwmon device, and registers line-card event callbacks. Each sysfs read/write builds the relevant register payload, calls `mlxsw_reg_query()` or `mlxsw_reg_write()`, and returns either a numeric sysfs value or a kernel error. On line-card activation, the callback initializes module and gearbox attributes for that slot and registers an additional hwmon device named `linecard#NN`; deactivation unregisters the device and resets its attribute count.

## State and Persistence
State is in memory only. The driver stores dynamic sysfs attributes in fixed-size arrays sized by maximum supported sensors/modules/gearboxes/fans and resets line-card `attrs_count` after unregister. Hardware sensor history is persistent in the device until `temp*_reset_history` sets `mte` and `mtr` in `MTMP`. PWM writes alter hardware fan duty through `MFSC`.

## Dependencies and Integration Points
The file depends on Linux hwmon/sysfs, SFP threshold constants, mlxsw register pack/unpack helpers, `core_env` module temperature threshold helpers, and line-card event registration. It cooperates with `core_linecards.c` so hot-plugged line cards gain telemetry only after the line-card manager marks them active.

## Risks
The dynamic attribute count must remain within `MLXSW_HWMON_ATTR_COUNT`; adding new attributes without updating count macros can overflow arrays. Gearbox sensor indexing is indirect through `mlxsw_hwmon_get_attr_index()` and modulo arithmetic, so off-by-one errors could query the wrong `MTMP` index. Line-card activation failures after partial attribute population do not explicitly clear `attrs_count` unless a device had been registered and later deactivated. Sysfs handlers return raw register errors, so hardware access failures surface directly to userspace.

## Test Signals
Useful tests include reading all generated `/sys/class/hwmon/.../temp*`, `fan*`, and `pwm*` attributes on systems with and without modules, writing valid and invalid PWM values, writing `1` and invalid values to reset-history attributes, unplugging/replugging line cards, and injecting `mlxsw_reg_query()` failures to verify cleanup paths. Kernel logs should show no attribute registration warnings and no use-after-free reports during line-card deactivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecard_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecard_dev.c

## Purpose
`core_linecard_dev.c` turns each provisioned mlxsw line card into an auxiliary bus device and attaches a nested devlink instance to it. This gives a line card its own devlink information and firmware flashing surface while the parent line-card manager owns provisioning and state transitions.

## Important APIs, Types, and Functions
- `struct mlxsw_linecard_bdev` embeds `struct auxiliary_device`, points at the owning `struct mlxsw_linecard`, and stores the allocated nested devlink private object.
- A global `IDA` allocates stable auxiliary device IDs. `mlxsw_linecard_bdev_release()` frees the ID and object after auxiliary-device lifetime ends.
- `mlxsw_linecard_bdev_add()` / `mlxsw_linecard_bdev_del()` are called by `core_linecards.c` when provisioning is set or cleared.
- `mlxsw_linecard_bdev_probe()` allocates a devlink with `mlxsw_linecard_dev_devlink_ops`, links it to the parent devlink linecard through `devlink_linecard_nested_dl_set()`, and registers it. Remove unregisters and frees that devlink.
- `mlxsw_linecard_driver_register()` / `mlxsw_linecard_driver_unregister()` wrap `auxiliary_driver_register()` and `auxiliary_driver_unregister()`.

## Control Flow
Provisioning allocates an ID, allocates and initializes an auxiliary device named `lc`, sets the parent to the mlxsw bus device, then adds it to the auxiliary bus. The auxiliary driver probe creates a nested devlink. Devlink `info_get` delegates to `mlxsw_linecard_devlink_info_get()`, while `flash_update` delegates to `mlxsw_linecard_flash_update()`. Unprovisioning deletes and uninitializes the auxiliary device; the release callback completes memory and ID cleanup.

## State and Persistence
The file persists only kernel object lifetime state: auxiliary ID allocation, parent/child device references, `linecard->bdev`, and the nested devlink private pointer. Firmware state and line-card readiness live in `core_linecards.c` and hardware.

## Dependencies and Integration Points
It depends on the auxiliary bus, devlink, IDA, and the line-card APIs exported by `core_linecards.c`. It is the bridge between devlink's nested line-card model and mlxsw's internal line-card object.

## Risks
The nested devlink is only valid after probe completes; call sites must tolerate line cards that are provisioned but whose auxiliary probe failed. `mlxsw_linecard_bdev_del()` must be idempotent because unprovisioned cards do not have `bdev`. Lifetime correctness depends on using auxiliary device delete/uninit rather than freeing directly.

## Test Signals
Provision/unprovision a line card and verify auxiliary device creation/removal, nested devlink visibility, `devlink dev info` output, and line-card `devlink flash` delegation. Error-path tests should cover ID allocation failure, `auxiliary_device_init()` failure, `auxiliary_device_add()` failure, and `devlink_linecard_nested_dl_set()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecard_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecards.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecards.c

## Purpose
`core_linecards.c` is the central line-card manager for modular mlxsw systems. It discovers available slots, parses optional line-card INI bundle firmware, exposes devlink linecard operations, transfers INI data to hardware, tracks provisioned/ready/active state, dispatches active/inactive notifications to other subsystems, and supports firmware flashing of flashable devices on active line cards.

## Important APIs, Types, and Functions
- `struct mlxsw_linecard_ini_file` models one INI blob in the `NVLCINI+` bundle. `struct mlxsw_linecard_types_info` owns the firmware buffer and parsed pointer table.
- Firmware flash support is implemented through `struct mlxsw_linecard_device_fw_info` and `mlxsw_linecard_device_dev_ops`, adapting mlxsw `MDDT` register accesses to the generic `mlxfw` FSM callbacks.
- Public functions include `mlxsw_linecard_flash_update()`, `mlxsw_linecard_devlink_info_get()`, `mlxsw_linecards_event_ops_register()`, `mlxsw_linecards_event_ops_unregister()`, `mlxsw_linecards_init()`, and `mlxsw_linecards_fini()`.
- Devlink linecard callbacks are `mlxsw_linecard_provision()`, `mlxsw_linecard_unprovision()`, `mlxsw_linecard_same_provision()`, `mlxsw_linecard_types_count()`, and `mlxsw_linecard_types_get()`.
- Event listeners use `DSDSC` for slot status and `BCTOE` for INI/BCT operation events, queueing work items that process copied register payloads outside interrupt context.

## Control Flow
Initialization queries `MGPIR` for slot count and exits early on non-modular systems. For modular systems it allocates `struct mlxsw_linecards`, optionally loads `mellanox/lc_ini_bundle_<minor>_<subminor>.bin`, registers traps and IRQ event handling, sets the core linecards pointer, creates one devlink linecard per slot, and enables event delivery per slot. Provisioning erases current INI, transfers the selected INI in `MBCT` chunks, schedules a timeout for the expected provision status event, and activates the image. Hardware status events call `mlxsw_linecard_status_process()`, which serializes on the linecard lock and transitions provisioned, ready, and active flags in order. Active transitions notify registered subscribers such as hwmon, thermal, and the minimal driver.

## State and Persistence
Per-linecard state includes slot index, devlink linecard pointer, `provisioned`, `ready`, `active`, hardware and INI revisions, the selected flashable device info/index, a delayed timeout work item, and a scratch `MBCT` payload. Global linecards state includes count, core/bus pointers, parsed type info, and a list of event-ops subscribers. Persistent hardware effects include INI erase/transfer/activation, firmware flash FSM operations, and ready bit changes through `MDDC`.

## Dependencies and Integration Points
The manager depends on devlink linecard APIs, workqueues, mlxsw core trap/event plumbing, mlxsw register helpers (`MDDQ`, `MDDT`, `MDDC`, `MBCT`, `MCQI`, `MCC`, `MCDA`, `MGIR`), generic `mlxfw`, request_firmware, and auxiliary-device glue in `core_linecard_dev.c`. It is consumed by hwmon, thermal, and minimal port handling through event ops and by core port removal through `mlxsw_core_ports_remove_selected()`.

## Risks
The status process must maintain transition order: provision before ready/active, deactivate before ready/provision clear. A missed status event triggers delayed failure, so timeout scheduling and cancellation must stay balanced. INI bundle parsing mutates copied firmware data by swabbing u32 words; validation must reject truncated or non-4-byte-aligned INIs first. Firmware flashing is allowed only for active line cards under the linecard lock. Event-op unregister calls inactive callbacks after removing the list item, so consumers must tolerate callbacks during teardown.

## Test Signals
Exercise modular and non-modular boots, missing and invalid INI bundle files, devlink type enumeration, provision/unprovision with successful DSDSC events, provision timeout, BCT activation failure, active/inactive notifications to hwmon/thermal/minimal, nested devlink info and flash, and teardown while delayed work or queued status/BCT work exists. Fault injection around register writes should leave devlink linecard state failed rather than partially active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_linecards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_thermal.c

## Purpose
`core_thermal.c` registers thermal zones and cooling devices for mlxsw ASIC, modules, gearboxes, and line cards. It maps hardware temperature registers into Linux thermal-zone callbacks and maps PWM controls into thermal cooling-device states.

## Important APIs, Types, and Functions
- `struct mlxsw_thermal` owns the main ASIC thermal zone, PWM cooling devices, trip tables, cooling state ranges, and a flexible array of board/line-card thermal areas.
- `struct mlxsw_thermal_area` groups module and gearbox thermal zones for one slot. `struct mlxsw_thermal_module` stores one module/gearbox thermal zone, copied trip table, cooling-state table, module index, and slot index.
- Thermal callbacks include `mlxsw_thermal_get_temp()`, `mlxsw_thermal_module_temp_get()`, `mlxsw_thermal_gearbox_temp_get()`, and `should_bind` variants.
- Cooling callbacks `mlxsw_thermal_get_max_state()`, `mlxsw_thermal_get_cur_state()`, and `mlxsw_thermal_set_cur_state()` translate between thermal state `0..10` and `MFSC` PWM duty `0..255`.
- Lifecycle is `mlxsw_thermal_init()` / `mlxsw_thermal_fini()`, with line-card activation handled by `mlxsw_thermal_got_active()` / `mlxsw_thermal_got_inactive()`.

## Control Flow
Initialization queries slot count, allocates thermal state, copies default trip/cooling tables, queries fan capabilities, zeroes tachometer minimum RPM through `MFSL`, registers one cooling device per active PWM, sets polling delay based on `bus_info->low_frequency`, registers the main `mlxsw` thermal zone, initializes module and gearbox zones for slot 0, registers line-card event ops, then enables the main thermal zone. Module and gearbox init query `MGPIR`, allocate arrays, register named thermal zones, and enable them. Line-card active/inactive events create and destroy the slot's module/gearbox zones.

## State and Persistence
Thermal trips and cooling-state mappings are per-zone in memory and include writable trip temperatures. PWM state is persisted in hardware via `MFSC`. Tachometer minimum RPM is adjusted in hardware during init. Zone registrations and line-card active flags are runtime state only.

## Dependencies and Integration Points
The file depends on Linux thermal framework, mlxsw register access (`MTMP`, `MFCR`, `MFSC`, `MFSL`, `MGPIR`), SFP constants for module thermal defaults, and line-card event registration. It intentionally sets `.no_hwmon = true` because hwmon exposure is handled separately by `core_hwmon.c`.

## Risks
Cooling device binding allows named external devices (`mlxreg_fan`, `emc2305`) and indexes them as cooling device 0, so platform naming changes can affect thermal policy. `mlxsw_thermal_set_cur_state()` clamps nonzero states to a minimum fan state, meaning requests below minimum still drive fans. Init error cleanup must unregister all possible cooling devices, including NULL entries. Line-card zone creation can partially fail and must unwind module zones when gearbox init fails.

## Test Signals
Validate `/sys/class/thermal` zones for ASIC, modules, gearboxes, and line cards; force thermal readings and verify trip binding; change PWM through thermal cooling state; boot low-frequency I2C systems and verify slow polling; hotplug line cards and check zone creation/destruction; inject failures in thermal zone and cooling device registration to confirm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/emad.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/emad.h

## Purpose
`emad.h` defines Ethernet Management Datagram constants shared by mlxsw code that builds, sends, receives, or diagnoses EMAD register-access frames. It contains frame sizing, Ethernet header constants, TLV type and length constants, operation classes, methods, and status decoding.

## Important APIs, Types, and Functions
- `MLXSW_EMAD_MAX_FRAME_LEN` and `MLXSW_EMAD_MAX_RETRY` define transport limits and retry behavior.
- Ethernet header constants define Mellanox multicast-like DMAC/SMAC, ethertype `0x8932`, protocol, and version.
- TLV enums cover END, OP, STRING, REG, and LATENCY TLVs. Operation enums cover request/response and query/write/send/event methods.
- `enum mlxsw_emad_op_tlv_status` enumerates device result codes.
- `mlxsw_emad_op_tlv_status_str()` converts status codes into diagnostic strings.

## Control Flow
This header has no runtime state or control flow beyond the inline status-string switch. It is included by EMAD handling code to keep protocol constants centralized.

## State and Persistence
No persistent state exists. Constants encode protocol layout and retry policy.

## Dependencies and Integration Points
The header is consumed by mlxsw core EMAD transport paths and register-access logic. It sits above bus implementations such as PCI and I2C because EMAD frames are carried over the bus transmit path.

## Risks
Protocol constants must match firmware expectations exactly. Unknown status codes map to `*UNKNOWN*`, so callers should log numeric status as well when available. Changing retry or frame-size constants can affect register-access reliability under busy firmware.

## Test Signals
Exercise EMAD query/write success, busy/ack retransmit handling, unsupported register/method/class errors, and unknown status logging. Packet captures or debug traces should show the expected ethertype, TLV order, and frame length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/emad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.c

## Purpose
`i2c.c` implements the mlxsw bus backend for switch ASICs reachable over I2C. It discovers local command mailboxes, executes command-register transactions through chunked I2C transfers, optionally forwards platform IRQs into mlxsw core event handling, and registers/unregisters I2C clients as mlxsw core bus devices.

## Important APIs, Types, and Functions
- `struct mlxsw_i2c` stores command mailbox offsets/sizes, a command mutex, device/core/bus info, selected I2C block size, platform hotplug data, IRQ work, and IRQ number.
- Low-level helpers include `mlxsw_i2c_set_slave_addr()`, `mlxsw_i2c_wait_go_bit()`, `mlxsw_i2c_write_cmd()`, `mlxsw_i2c_write_init_cmd()`, and `mlxsw_i2c_get_mbox()`.
- Command execution flows through `mlxsw_i2c_cmd()`, `mlxsw_i2c_write()`, and the bus callback `mlxsw_i2c_cmd_exec()`.
- Bus lifecycle callbacks are `mlxsw_i2c_init()` / `mlxsw_i2c_fini()`. Driver lifecycle is `mlxsw_i2c_probe()`, `mlxsw_i2c_remove()`, `mlxsw_i2c_driver_register()`, and `mlxsw_i2c_driver_unregister()`.
- `mlxsw_i2c_irq_init()` optionally requests a shared falling-edge IRQ and schedules `mlxsw_core_irq_event_handlers_call()` from workqueue context.

## Control Flow
Probe allocates private state, derives a safe block size from adapter quirks, sends an immediate `QUERY_FW` command to validate access, waits for the GO bit to clear, reads mailbox offsets from the command interface region, fills bus info, initializes optional IRQ support, and registers with mlxsw core. Command execution serializes on `cmd.lock`. With an input mailbox, it computes register TLV size, writes the mailbox in block-sized I2C chunks, posts an ACCESS_REG command, waits for completion, and optionally reads output chunks. Without an input mailbox, it issues an initialization/query command and reads a default-sized output buffer.

## State and Persistence
Runtime state includes mailbox offsets/sizes discovered from hardware, block size, command mutex, IRQ work, bus info, and core pointer. Hardware state includes command interface GO/status bits and mailbox contents. The bus is marked `low_frequency`, influencing slower thermal polling elsewhere.

## Dependencies and Integration Points
The file depends on Linux I2C, optional `CONFIG_MLXREG_HOTPLUG`, mlxsw command helpers, core bus registration, and resource query helpers. It exposes no packet transport: `skb_transmit_busy()` always false and `skb_transmit()` returns success without sending, so users are command/environment-oriented drivers such as `minimal.c`.

## Risks
Retry loops use a timeout OR retry-count condition, which can continue while either bound remains true; changes here should preserve intended tolerance without indefinite waits. Mailbox size is derived from the input TLV and must remain aligned to u32. Adapter quirks smaller than the default block size reject the device. IRQ handler returns `IRQ_NONE` because it shares the line with another handler; platform integration must expect that.

## Test Signals
Test I2C adapters with and without quirks, insufficient max read/write lengths, mailbox discovery, command read/write with multi-block payloads, GO-bit timeout/status error, optional IRQ delivery, and removal cleanup. Minimal-driver module EEPROM reads are practical end-to-end command-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.h

## Purpose
`i2c.h` declares the optional mlxsw I2C bus-driver registration interface used by mlxsw device drivers that bind over I2C.

## Important APIs, Types, and Functions
- When `CONFIG_MLXSW_I2C` is enabled, it declares `mlxsw_i2c_driver_register()` and `mlxsw_i2c_driver_unregister()`.
- When disabled, inline stubs make registration fail with `-ENODEV` and unregistration a no-op.

## Control Flow
There is no internal control flow beyond compile-time `IS_ENABLED(CONFIG_MLXSW_I2C)` selection. Callers such as `minimal.c` can compile regardless of whether the I2C backend is enabled.

## State and Persistence
No runtime state exists in this header.

## Dependencies and Integration Points
It depends on `<linux/i2c.h>` and is consumed by mlxsw drivers that want the common I2C probe/remove implementation installed into their `struct i2c_driver`.

## Risks
The disabled stub returns `-ENODEV`, so module init code must unwind any earlier registration when I2C support is absent. Any future registration API change must keep enabled and disabled branches signature-compatible.

## Test Signals
Build with `CONFIG_MLXSW_I2C=y/m` and disabled. For disabled builds, module init should fail cleanly after unregistering any previously registered mlxsw core driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/item.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/item.h

## Purpose
`item.h` is the generated-accessor foundation for mlxsw command, register, descriptor, CQE, EQE, and header layouts. It describes bitfields and buffers in big-endian hardware byte arrays and emits typed inline getters/setters through macros.

## Important APIs, Types, and Functions
- `struct mlxsw_item` describes offset, indexed step, shift, bit or byte size, optional "no real shift", element size for bit arrays, and a diagnostic name.
- Base helpers implement aligned offsets, big-endian `u8/u16/u32/u64` field extraction/insertion, buffer copies, direct data pointers, and bit-array element access.
- Macros `MLXSW_ITEM8/16/32/64`, `_INDEXED`, `MLXSW_ITEM32_LP`, `MLXSW_ITEM_BUF`, `MLXSW_ITEM_BUF_INDEXED`, and `MLXSW_ITEM_BIT_ARRAY` define one static item descriptor and inline accessors named `mlxsw_<type>_<container>_<item>_*`.

## Control Flow
Consumers include this header and instantiate accessors at compile time. Runtime helpers validate alignment and indexing with `BUG_ON()` / `WARN_ONCE()` before reading or writing byte buffers. Setters mask existing field bits, insert new values, and preserve unrelated bits.

## State and Persistence
The only state is static `struct mlxsw_item` descriptors generated by macros in each translation unit. The helpers mutate caller-provided hardware payload buffers; they do not own persistent data.

## Dependencies and Integration Points
It depends on Linux types, string helpers, and bit operations. It is heavily used by `pci_hw.h`, command mailbox definitions, register definitions, and tx header definitions to keep layout access consistent across the driver.

## Risks
Bad offsets, steps, shifts, or sizes in macro users can crash the kernel through `BUG()` or corrupt hardware payloads. Big-endian conversion is built in for multi-byte fields, so callers must pass raw hardware-format buffers, not host-ordered structs. Bit-array indexing intentionally reverses index order inside big-endian arrays; changes can silently break protocol layout.

## Test Signals
Compile coverage is important because macro output is generated per field. Unit-style tests can round-trip getters/setters on synthetic buffers for each width, indexed fields, local-port split fields, buffers, and bit arrays. Runtime debug should not emit "mlxsw: item bug" errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/minimal.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/minimal.c

## Purpose
`minimal.c` is a lightweight mlxsw driver for I2C-attached systems that need front-panel module access without full switch data-plane support. It creates simple Ethernet netdevs for modules, exposes ethtool module EEPROM/power/reset operations, maps modules to local ports, and responds to line-card activation/inactivation.

## Important APIs, Types, and Functions
- `struct mlxsw_m` stores core/bus references, base MAC, port table, slot/module topology, and line-card mapping arrays.
- `struct mlxsw_m_port` is netdev private data tying a netdev to local port, slot, module, and module offset.
- Port operations are `mlxsw_m_port_open()` and `mlxsw_m_port_stop()`, delegating to `mlxsw_env_module_port_up()` / `_down()`.
- Ethtool operations expose driver info, EEPROM, page-based EEPROM read/write, module reset, and module power mode through `core_env` helpers.
- Initialization and teardown are `mlxsw_m_init()` / `mlxsw_m_fini()`, registered through `struct mlxsw_driver`; module init also registers an I2C driver through `mlxsw_i2c_driver_register()`.

## Control Flow
Driver init validates minimum firmware minor/subminor, reads base MAC, allocates topology arrays, registers line-card event callbacks, maps modules to local ports by querying `PMLP`, and creates netdevs for the main board. Each port creation initializes the core port, allocates an etherdev, links it to mlxsw core, derives its MAC from `PPAD`, and registers the netdev. Line-card active callbacks remap ports and create netdevs for that slot; inactive callbacks remove those netdevs and unmap modules. Module exit unregisters the I2C backend and the mlxsw core driver.

## State and Persistence
State is in-memory: `ports[local_port]`, per-slot `module_to_port[]` arrays initialized to `-1`, active flags per slot, and base MAC. Hardware-visible state includes module-to-port maps, module port up/down state, and any EEPROM/power/reset operations requested via ethtool.

## Dependencies and Integration Points
The file depends on the common mlxsw core driver model, I2C bus backend, `core_env` module helpers, devlink line-card events from `core_linecards.c`, netdev registration, and ethtool module APIs. It provides `ports_remove_selected` so line-card unprovisioning can remove ports for one slot.

## Risks
The line-card active flag is used both to skip duplicate mapping and to drive removal assertions; incorrect flag sequencing can leak netdevs or skip new ports. Module offset math assumes uniform maximum modules per line card. `mlxsw_m_port_open()` and `stop()` pass slot `0` in this source for port up/down, while other module operations use `slot_index`; that is a detail to verify against intended hardware semantics. Port mapping skips width-zero and clustered duplicate modules by tracking `last_module`.

## Test Signals
Boot an I2C minimal device and verify firmware compatibility checks, netdev creation for all mapped modules, ethtool EEPROM/page/power/reset operations, line-card hotplug netdev creation/removal, module-to-port unmap on teardown, and clean unwind when a port registration fails mid-slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/minimal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.c

## Purpose
`pci.c` implements the high-performance mlxsw PCI bus backend. It owns PCI probe/remove/reset handling, command-register execution, firmware area mapping, async send/receive/completion/event queues, DMA mapping, NAPI processing, packet transmit/receive handoff, profile configuration, resource discovery, clock reads, and integration with the mlxsw core bus.

## Important APIs, Types, and Functions
- `struct mlxsw_pci` stores PCI device state, BAR mapping, queue groups, FW area pages, command mailboxes, bus info, capabilities, profile-selected modes, CQE version, SDQ/CQ counts, reset behavior, and dummy NAPI netdevs.
- Queue structures are `struct mlxsw_pci_queue`, `struct mlxsw_pci_queue_elem_info`, `struct mlxsw_pci_queue_type_group`, and queue ops tables for SDQ, RDQ, CQ, and EQ.
- Initialization paths include `mlxsw_pci_probe()`, `mlxsw_pci_cmd_init()`, bus callback `mlxsw_pci_init()`, `mlxsw_pci_reset()`, `mlxsw_pci_fw_area_init()`, `mlxsw_pci_config_profile()`, `mlxsw_pci_aqs_init()`, and per-queue init functions.
- Data paths include `mlxsw_pci_skb_transmit()`, `mlxsw_pci_cqe_sdq_handle()`, `mlxsw_pci_cqe_rdq_handle()`, `mlxsw_pci_napi_poll_cq_tx()`, `mlxsw_pci_napi_poll_cq_rx()`, and `mlxsw_pci_eq_tasklet()`.
- Command execution is `mlxsw_pci_cmd_exec()`, which serializes command registers, maps in/out mailboxes, polls GO bit, and copies direct or mailbox output.

## Control Flow
PCI probe allocates private state, enables the function, requests regions, sets DMA mask, maps BAR0, initializes command mailboxes, fills bus info, and registers the mlxsw bus. The bus init waits for system readiness, resets hardware unless recovery already did, allocates MSI-X, queries firmware, validates command interface/BAR expectations, maps firmware area pages, reads board info, queries resources, chooses CQE version, configures profile and modes, re-queries resources, initializes NAPI dummy devices, allocates EQ/CQ/SDQ/RDQ queue groups, and requests the EQ IRQ. EQ interrupts schedule a tasklet, the tasklet records active CQs and schedules their NAPI instances, NAPI drains CQEs, and CQ handlers process transmit completions or received packets.

## State and Persistence
Persistent runtime state includes DMA coherent queue memory, page-pool pages for receive WQEs, command mailboxes, firmware-area pages mapped to hardware, producer/consumer counters, owner-bit parity, skb pointers stored in SDQ element info, selected LAG/flood modes, clock offsets, and bus capabilities. Hardware state includes reset mode, config profile, queue ownership, doorbells, firmware area mappings, and command-register state.

## Dependencies and Integration Points
The file depends on Linux PCI/MSI-X/IRQ/tasklet/NAPI/page_pool/DMA APIs, mlxsw command mailbox helpers, `pci_hw.h` descriptor accessors, core bus registration, core packet receive/transmit callbacks, PTP timestamp handling, resource queries, tx header helpers, and port constants. It exports `mlxsw_pci_driver_register()` and `mlxsw_pci_driver_unregister()` so chip-specific PCI drivers can reuse this backend.

## Risks
Queue ownership and producer/consumer counters are subtle; incorrect owner-bit parity, missing barriers, or wrong doorbell order can cause lost completions or DMA races. Receive page replacement happens before skb construction, so allocation failure must recycle old pages correctly. `mlxsw_pci_skb_transmit()` must unmap all mapped fragments on partial failure and avoid leaking the skb pointer on failed first-fragment mapping. Reset and PCI error recovery paths must avoid double reset by using `skip_reset`. CQE version negotiation affects descriptor sizes and accessors; unsupported resource combinations abort init.

## Test Signals
Test PCI probe/remove, reset and PCI error recovery, command timeout/status errors, resource combinations for CQE v0/v1/v2, profile LAG/flood mode choices, TX queue full/EAGAIN behavior, TX completion DMA unmap and timestamp delivery, RX multi-fragment packets, mirror/sample metadata extraction, page-pool recycling under allocation failure, MSI-X EQ scheduling, NAPI budget behavior, and teardown with active queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.h

## Purpose
`pci.h` declares PCI device IDs for Mellanox Spectrum ASIC generations and exposes the optional common PCI backend registration interface.

## Important APIs, Types, and Functions
- Defines `PCI_DEVICE_ID_MELLANOX_SPECTRUM`, `SPECTRUM2`, `SPECTRUM3`, and `SPECTRUM4`.
- When `CONFIG_MLXSW_PCI` is enabled, declares `mlxsw_pci_driver_register()` and `mlxsw_pci_driver_unregister()`.
- When disabled, provides no-op-ish stubs: register returns `0`, unregister does nothing.

## Control Flow
The header is compile-time glue only. Chip drivers pass their `struct pci_driver` to the common registration helper so `pci.c` can install probe/remove/shutdown/error handlers.

## State and Persistence
No runtime state exists in this header.

## Dependencies and Integration Points
It depends on `<linux/pci.h>` and is included by mlxsw PCI chip drivers and `pci.c`. The IDs connect modalias matching to supported Spectrum devices.

## Risks
The disabled registration stub returns success, unlike the I2C stub, so callers must be aware that a build without `CONFIG_MLXSW_PCI` may appear to register successfully at compile-time abstraction level. New Spectrum IDs must be added consistently with chip-specific driver ID tables.

## Test Signals
Build with PCI enabled/disabled and verify chip drivers compile. Runtime PCI modalias matching should bind supported Spectrum IDs to drivers that use this backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci_hw.h

## Purpose
`pci_hw.h` defines PCI hardware constants and descriptor/CQE/EQE layout accessors for the mlxsw PCI backend. It centralizes BAR sizing, command-interface register offsets, reset timing, doorbell offsets, queue limits, descriptor sizes, WQE fields, CQE version handling, mirror metadata, timestamps, and EQE fields.

## Important APIs, Types, and Functions
- Constants define BAR0 size, page size, CIR register offsets/bits/status shift, reset wait/timeout, FW-ready register/magic, doorbell regions, queue counts, descriptor sizes, and scatter/gather limits.
- WQE accessors define completion, local-processing, type, checksum, byte-count, and DMA-address fields.
- `enum mlxsw_pci_cqe_v` distinguishes CQE v0/v1/v2. `mlxsw_pci_cqe_item_helpers()` dispatches version-specific field accessors.
- CQE accessors cover ingress source, LAG fields, WQE counter, byte count, trap ID, CRC/error/send flags, descriptor queue, mirror congestion/class/latency/reason, TX source metadata, ACL cookie/original length, owner bit, and timestamp fields.
- Inline helpers combine split fields such as mirror congestion and timestamp seconds/nanoseconds.
- EQE accessors cover event type/subtype, completion queue number, owner bit, command token/status, and command output parameters.

## Control Flow
This header has no standalone runtime flow. `pci.c` calls the generated accessors when setting WQEs, interpreting CQEs, polling owner bits, decoding mirror/sample metadata, and handling EQ events.

## State and Persistence
The header defines static item descriptors in the including translation unit and mutates caller-owned DMA buffers through generated accessors. Hardware queue memory layout is the persistent contract.

## Dependencies and Integration Points
It depends on `item.h` for generated accessors and on Linux bit operations. It is tightly coupled to `pci.c` queue setup and data-path code, and to firmware-reported CQE version support.

## Risks
Any field offset/shift mismatch breaks DMA descriptor interpretation. CQE v2 is larger than v0/v1; queue element size/count must match firmware AQ capabilities. Owner-bit accessor selection must match queue CQE version or NAPI can either miss completions or read hardware-owned entries. Timestamp/mirror metadata invalid sentinel values must be honored by callers.

## Test Signals
Use synthetic descriptor buffers to round-trip key WQE/CQE/EQE fields. Runtime validation includes TX/RX traffic over CQE v0/v1/v2 hardware, mirror and sample traps with metadata, PTP timestamps, command EQEs, and queue owner-bit transitions across wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/pci_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/port.h

## Purpose
`port.h` provides shared mlxsw port constants and small enums for administrative and operational port status. It is included by bus and driver code that needs common limits or status values without pulling in larger port implementation headers.

## Important APIs, Types, and Functions
- Constants define maximum MTU, Ethernet frame overhead, default VLAN ID, SWID special values and types, InfiniBand port limits, CPU port, and don't-care sentinel.
- `enum mlxsw_port_admin_status` models admin up/down/up-once/disabled values.
- `enum mlxsw_reg_pude_oper_status` models operational up/down/failure states.

## Control Flow
No runtime control flow exists. The file is a constants header.

## State and Persistence
No state is stored. Values are consumed by register-packing and driver policy code.

## Dependencies and Integration Points
It depends on Linux types and is used by PCI code for MTU-derived scatter/gather sizing and by other mlxsw port/register code for common status constants.

## Risks
Changing `MLXSW_PORT_MAX_MTU` affects PCI receive scatter/gather sizing and queue buffer assumptions. Status enum values must match hardware register definitions.

## Test Signals
Build coverage plus runtime max-MTU packet tests are the primary signals. Register tests should confirm admin and operational status values match firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/port.h -->
