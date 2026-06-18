# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/smem.c

## Purpose
Queries firmware for shared-memory configuration and caches FIFO sizes and internal TX FIFO information in `iwl_fw_runtime`.

## Important APIs, Types, and Functions
The exported API is `iwl_get_shared_mem_conf()`. Internal parsers are `iwl_parse_shared_mem_22000()` for 22000/newer multi-LMAC formats and `iwl_parse_shared_mem()` for older shared-memory notifications.

## Control Flow
`iwl_get_shared_mem_conf()` selects `WIDE_ID(SYSTEM_GROUP, SHARED_MEM_CFG_CMD)` when extended shared-memory capability exists, otherwise the legacy `SHARED_MEM_CFG`. It sends a synchronous command with `CMD_WANT_SKB`, dispatches to the parser based on device family, logs success, and frees the response.

## State and Persistence Behavior
The command response fills `fwrt->smem_cfg`: LMAC count, TX FIFO entries, per-LMAC TX/RX FIFO sizes, RX FIFO 2 size, optional RX FIFO 2 control size, and internal TX FIFO address/sizes. The cache lasts for the firmware runtime and drives debug/TX FIFO iteration.

## Dependencies and Integration Points
Depends on `iwl_trans_send_cmd`, response SKB ownership, firmware notification version lookup, capability checks, and shared-memory structures from `fw/api/commands.h`.

## Risks
Bad firmware lengths or advertised LMAC counts must not overflow `MAX_NUM_LMAC`. The 22000 parser only reads `rxfifo2_control_size` when notification version and payload length allow it. RF-kill failures are tolerated without warning.

## Test Signals
Legacy and extended command IDs, 22000 multi-LMAC parsing, payload-short warning, invalid LMAC count, RF-kill command failure, internal TX FIFO capability presence/absence, and response freeing are the main test points.
