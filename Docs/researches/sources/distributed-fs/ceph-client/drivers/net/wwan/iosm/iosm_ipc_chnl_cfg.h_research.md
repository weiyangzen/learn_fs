# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.h

## Purpose
Declares IOSM IPC channel IDs, trace channel sizing constants, `struct ipc_chnl_cfg`, and `ipc_chnl_cfg_get()`.

## Important APIs, Types, And Functions
Defines `IPC_MEM_TDS_TRC`, `IPC_MEM_MAX_DL_TRC_BUF_SIZE`, `enum ipc_channel_id` from IP channel 0 through control channel 7, and `struct ipc_chnl_cfg` fields for interface ID, uplink/downlink pipes, TD counts, downlink buffer size, WWAN port type, and accumulation backoff.

## Control Flow
No independent runtime flow. Callers allocate or stack-initialize `ipc_chnl_cfg` and call `ipc_chnl_cfg_get()` before creating IOSM IPC channels.

## State And Persistence
The struct carries copied configuration into channel initialization and persists according to caller storage.

## Dependencies And Integration Points
Includes `iosm_ipc_mux.h` for mux constants and is used by IOSM IMEM/devlink/channel setup code.

## Risks
Enum values are used as array indices in the C file, so reordering changes behavior. The comment says `index` is up to MAX_CHANNELS, but no max symbol is declared here.

## Test Signals
Build consumers after enum/table changes, and validate channel setup for mux, AT, trace, MBIM, loopback, and flash/coredump.
