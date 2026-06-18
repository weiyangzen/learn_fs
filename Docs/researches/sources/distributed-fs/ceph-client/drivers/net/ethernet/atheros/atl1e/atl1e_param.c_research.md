# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e_param.c

## Purpose
Implements ATL1E module parameter parsing and validation. It converts per-board integer module options into adapter defaults for TX descriptor count, RX memory size, interrupt moderation, and media type before the main driver initializes rings and hardware configuration.

## Important APIs, Types, and Functions
The `ATL1E_PARAM` macro declares integer module-parameter arrays for up to `ATL1E_MAX_NIC` boards. Defined parameters are `tx_desc_cnt`, `rx_mem_size`, `media_type`, and `int_mod_timer`. `struct atl1e_option` describes an option as enable/range/list with default and bounds. `atl1e_validate_option` applies defaulting, range/list checks, and netdev logging. `atl1e_check_options` is the exported entry point called during probe.

## Control Flow and State
`atl1e_check_options` uses `adapter->bd_number` to select the per-board array element. Missing or unset entries fall back to defaults. Validated values are written into runtime adapter state: `adapter->tx_ring.count`, `adapter->rx_ring.page_size`, `adapter->hw.imt`, and `adapter->hw.media_type`. TX descriptor count is masked with `0xFFFC`, aligning the count down to a multiple of four. RX memory size is converted from KB to bytes. Invalid values are logged and replaced with defaults.

State persists only in static module parameter arrays and in fields of the probed adapter. There is no dynamic allocation or hardware access in this file; hardware effects occur later when `atl1e_main.c` sizes rings and writes interrupt/link configuration.

## Dependencies and Integration Points
Includes `linux/netdevice.h` and `atl1e.h`. Integrates with the module loader through `module_param_array_named` and `MODULE_PARM_DESC`, and with probe through `atl1e_check_options(adapter)`. The media type constants and flow-control defaults are consumed by hardware link setup in other ATL1E files.

## Risks
The parameter arrays are fixed-size and board-indexed. Boards beyond `ATL1E_MAX_NIC` are logged as defaulted, but the code still checks `num_* > bd`; maintaining that guard is important for array safety. Range comments do not exactly match all constants, so behavior should be based on constants rather than comments. The aligned-down TX descriptor count may surprise users near the minimum and should stay compatible with ring-size hardware requirements. Too-small RX memory or interrupt moderation settings can affect throughput/latency and expose RX page wrap behavior in `atl1e_main.c`.

## Test Signals
Load the module with default parameters, with valid per-board arrays, with out-of-range values, and with more NICs than configured. Confirm logs report validation/defaulting, ring sizes reflect expected values, interrupt moderation register programming uses `hw.imt`, and forced media settings affect link advertisement/reset behavior. Build tests should catch changes to media constants or adapter field names.
