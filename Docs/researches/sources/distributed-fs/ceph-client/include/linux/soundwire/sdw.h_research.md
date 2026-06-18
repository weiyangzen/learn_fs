<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h

Purpose: This is the central Linux SoundWire bus API. It defines SoundWire protocol constants, slave/master properties, device and bus objects, stream lifecycle state, bus parameters, driver callback tables, BPT helpers, messaging APIs, and disabled-config stubs.

Important APIs/types/functions: Core types include `sdw_slave`, `sdw_bus`, `sdw_master_device`, `sdw_driver`, `sdw_stream_runtime`, `sdw_stream_config`, `sdw_port_config`, `sdw_bus_params`, `sdw_slave_prop`, `sdw_master_prop`, and callback tables `sdw_slave_ops`, `sdw_master_ops`, and `sdw_master_port_ops`. Public APIs cover bus add/delete, property parsing, stream allocation/release/add/remove/prepare/enable/disable/deprepare, clock stop/exit, slave ID extraction, BPT send/wait, and register read/write/update.

Control flow: A master driver creates an `sdw_bus`, provides master/port ops, and registers it. Slave drivers bind through `sdw_driver` and optionally implement property, status, interrupt, bus config, port prep, and clock-stop callbacks. Stream control moves through `ALLOCATED -> CONFIGURED -> PREPARED -> ENABLED -> DISABLED -> DEPREPARED -> RELEASED`; bus parameter computation feeds frame shape, bandwidth, bank switching, and port programming.

State and persistence: `sdw_bus` holds locks, slave lists, runtime stream lists, deferred messages, current/next bank, assigned device-number bitmap, clock/bank-switch timeouts, IRQ domain/chip, stream/BPT refcounts, and lane bandwidth. `sdw_slave` holds status, sticky and current device numbers, completions for enumeration/initialization/port readiness, first-interrupt flags, unattach reasons, and SDCA data.

Dependencies/integration: Integrates with the driver core, fwnode/OF, IRQ domains, debugfs, SDCA helpers, ASoC stream users, PM/clock-stop paths, and vendor master drivers. `CONFIG_SOUNDWIRE` stubs warn once and return errors when disabled.

Risks and test signals: Risks include stream state misuse, bank mismatch, enumeration/read races, missed completions, device-number leaks, BPT multiple-stream violations, and callbacks racing with remove. Test with SoundWire codec enumeration, stream prepare/enable/deprepare ordering, suspend/resume clock-stop modes, interrupt routing, debugfs status, no-PM register access, and disabled-config compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw.h -->
