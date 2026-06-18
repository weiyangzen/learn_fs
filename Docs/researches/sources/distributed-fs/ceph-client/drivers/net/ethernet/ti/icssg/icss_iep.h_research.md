# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.h

## Purpose
`icss_iep.h` defines the public ICSS IEP timer interface for PRU/ICSSG Ethernet drivers. It provides logical register IDs, platform-data shape, runtime state, firmware clockops, and exported function prototypes.

## Important APIs, Types, and Functions
The register enum gives stable logical IDs for global config/status, compensation, count, capture, compare, sync, period, delay, and start registers; SoC-specific code maps those IDs to offsets. `struct icss_iep_plat_data` holds a regmap config, offset table, and feature flags. `struct icss_iep` holds device and MMIO state, regmap, exclusive client node, reference clock data, PHC info/clock, mutex, increment/compensation fields, optional firmware `struct icss_iep_clockops`, cycle time, PPS/perout/latch state, IRQ, period, and work item. `struct icss_iep_clockops` lets firmware-specific users override settime, adjtime, gettime, perout, and external timestamp behavior.

## Control Flow and State
Consumers obtain an IEP with `icss_iep_get()` or indexed `icss_iep_get_idx()`, initialize either raw firmware mode with `icss_iep_init_fw()` or PHC mode with `icss_iep_init()`, query counts/PHC index, then call exit and put in reverse. The state is intentionally not opaque; ICSSG code can inspect fields such as `ptp_clock`, but should respect `ptp_clk_mutex` for clock operations and exclusive ownership through `client_np`.

## Dependencies and Integration Points
The header depends on mutex, PTP clock kernel, and regmap types. It is included by `icss_iep.c` and ICSSG Ethernet files needing PTP and firmware timer integration. `prueth_iep_clockops` is declared here for the PRU Ethernet implementation.

## Risks and Test Signals
Because `struct icss_iep` is exposed, changes to field names or semantics can break companion drivers. Register enum additions must remain synchronized with all offset tables in `icss_iep.c`. Tests should cover build integration for PHC and firmware users, indexed phandle acquisition, and feature combinations where perout, PPS, external timestamp, or 64-bit counters are unavailable.
