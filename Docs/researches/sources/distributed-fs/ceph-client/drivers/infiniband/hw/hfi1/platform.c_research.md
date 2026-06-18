# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.c

## Purpose
`platform.c` loads platform configuration data, derives port/cable policy, qualifies QSFP modules, and applies link SerDes/QSFP tuning before HFI1 link negotiation. It combines BIOS scratch data, EPROM or firmware platform tables, QSFP memory, and 8051 firmware configuration commands.

## Important APIs, Types, And Functions
`get_platform_config()` obtains config from integrated-platform scratch registers, EPROM, or fallback firmware `hfi1_platform.dat`; `free_platform_config()` releases copied data; `get_port_type()` reads the configured port type. `set_qsfp_tx()` controls QSFP transmitter disable bits. `qual_power()` and `qual_bitrate()` enforce power-class and speed policies. `set_qsfp_high_power()`, `apply_cdr_settings()`, `apply_eq_settings()`, and `apply_rx_amplitude_settings()` program active QSFP modules. `apply_tunings()` sends tuning method, channel loss, external device capability, and TX EQ settings to the 8051. `tune_serdes()` is the top-level link-readiness workflow.

## Control Flow
Integrated systems first validate an ASIC scratch checksum and save prepacked fields; discrete systems try EPROM, then fallback firmware. During link setup, `tune_serdes()` clears link-ready state, handles loopback/simulator bypass, switches on `port_type`, verifies QSFP presence where required, locks the QSFP I2C resource, refreshes cache, tunes active or passive modules, refreshes cache after modifications, releases the resource, applies 8051 tunings if no offline-disabled reason was set, and finally marks `driver_link_ready`.

## State And Persistence
Platform data is kept in `dd->platform_config` or, for integrated scratch configs, decoded into `ppd` fields with `config_from_scratch`. Runtime port state includes `port_type`, attenuation values, preset bitmaps, max power class, QSFP cache flags, `offline_disabled_reason`, `link_enabled`, and `driver_link_ready`. QSFP module memory may be modified for power, CDR, EQ, TX disable, and amplitude settings; these changes are module runtime state and are reset via QSFP reset or cable removal.

## Dependencies And Integration Points
The file depends on EPROM access, firmware loading, platform-table parsing (`get_platform_config_field()`), QSFP read/write/cache helpers, chip resource locking, 8051 host-command config, OPA link speed/width policy constants, loopback/simulator flags, and port link startup code that consumes `driver_link_ready`.

## Risks
Many `get_platform_config_field()` calls in tuning paths log or continue with zero-initialized defaults, so malformed tables can silently lead to suboptimal or wrong tuning. Active QSFP programming changes module memory and relies on `reset_needed` to avoid stale settings across retunes. Power and bitrate failures communicate through `offline_disabled_reason`; ordering matters when multiple policies could apply. Several QSFP writes ignore return values, especially for CDR/EQ helpers.

## Test Signals
Test scratch checksum valid/invalid, EPROM success/failure, fallback firmware absence, each port type, QSFP absent/present/cache invalid, active/passive/unknown module technologies, power-class limits, bitrate rejection, high-power enable classes, CDR/EQ/amplitude support matrices, 8051 command failures, loopback bypass, and final `driver_link_ready`/offline reason transitions.
