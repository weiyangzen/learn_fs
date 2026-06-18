# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.c

## Purpose
Provides the IOSM modem IPC channel configuration table and a helper to copy a channel's pipe, descriptor, buffer, WWAN port, and IRQ accumulation settings to callers.

## Important APIs, Types, And Functions
Exports `ipc_chnl_cfg_get()`. The static `modem_cfg[]` table describes IP mux, RPC, AT, trace, loopback, MBIM, and flash/coredump channels. Local constants define maximum downlink buffer sizes, transfer descriptor counts, and accumulation backoff values.

## Control Flow
Callers pass a channel index. `ipc_chnl_cfg_get()` bounds-checks it, assigns mux-specific accumulation backoff for `IPC_MEM_MUX_IP_CH_IF_ID`, otherwise disables backoff, then copies the corresponding `modem_cfg` fields to the output struct.

## State And Persistence
The channel table is static read-mostly configuration. No dynamic state is retained. Output state is persisted by callers such as IMEM channel initialization.

## Dependencies And Integration Points
Depends on WWAN port type constants and IOSM mux constants from `iosm_ipc_mux.h`. Used by IOSM setup paths, including devlink flash/coredump channel initialization.

## Risks
`index` is checked only for upper bound; negative values would index before the array if passed. Channel zero is noted as reserved for flash, but the first table entry is IP mux and flash/coredump appears at control channel ID 7, so callers must use the intended enum/index consistently. Buffer sizes and TD counts directly affect DMA ring sizing and memory use.

## Test Signals
Exercise every valid channel index, invalid high index, and ideally negative-index hardening. Verify WWAN port exposure for AT/RPC/MBIM and flash/coredump channel operation through devlink.
