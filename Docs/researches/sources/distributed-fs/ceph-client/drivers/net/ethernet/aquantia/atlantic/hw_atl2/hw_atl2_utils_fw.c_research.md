# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_utils_fw.c

## Purpose
This file implements the A2 firmware operations table `aq_a2_fw_ops`. It translates Atlantic driver firmware hooks into reads and writes of the A2 shared-buffer ABI, including link control, EEE, pause, link status, stats, MAC address, WoL sleep proxy, temperature, loopback, downshift, firmware version, and ART capability queries.

## Important APIs, types, and functions
The exported symbols are `hw_atl2_utils_get_fw_version`, `hw_atl2_utils_get_action_resolve_table_caps`, and `const struct aq_fw_ops aq_a2_fw_ops`. Important internal helpers are the shared-buffer access macros, `hw_atl2_shared_buffer_read_block`, `hw_atl2_shared_buffer_finish_ack`, `aq_a2_fw_init`, `aq_a2_fw_deinit`, `aq_a2_fw_set_link_speed`, `aq_a2_fw_set_state`, `aq_a2_fw_update_link_status`, `aq_a2_fw_update_stats`, `aq_a2_fill_a0_stats`, `aq_a2_fill_b0_stats`, `aq_a2_fw_set_wol_params`, `aq_a2_fw_set_eee_rate`, `aq_a2_fw_get_eee_rate`, `aq_a2_fw_renegotiate`, `aq_a2_fw_set_flow_control`, `aq_a2_fw_get_flow_control`, `aq_a2_fw_set_phyloopback`, and `aq_a2_fw_set_downshift`.

## Control flow
Single-dword reads use `hw_atl2_shared_buffer_read`; multiword reads use transaction counters and retry until both counters match before and after the read. Writes update `fw_interface_in` fields, then set the host-finished bit and poll for MCP acknowledgement. Init sets host mode active and jumbo MTU; deinit switches to shutdown. Link setup writes `link_options`, while `MPI_INIT` also sets EEE and pause bits. Stats read firmware version to choose A0 or B0 stats layout, compute deltas against `priv->last_stats`, then combine firmware stats with DMA hardware counters.

## State and persistence
The file updates firmware shared input state and driver state in `aq_link_status`, `curr_stats`, and `hw_atl2_priv.last_stats`. WoL programming changes MAC address, sleep proxy wake flags, and host mode. Firmware output state is treated as authoritative for link partner caps, flow control, device caps, and temperature.

## Dependencies and integration points
It depends on `hw_atl2_utils.h` ABI structs, `hw_atl2_llh` shared-buffer helpers, B0 stats register helpers, `aq_nic_cfg_s`, and the generic `aq_fw_ops` interface consumed by ATL2 hardware ops.

## Risks
Multiword reads can return `-ETIME` if firmware transaction counters keep changing or never stabilize. Stats deltas are ignored when a negative/corrupt delta is detected, and stats only accumulate while link is up. `hw_atl2_utils_get_fw_version` ignores the return from `read_safe`. The sleep proxy write uses a nested `wake_on_lan_s` object with the `sleep_proxy` field macro, so layout assumptions are especially important.

## Test signals
Exercise link up/down, advertised speeds including 10M through 10G, EEE set/get, pause set/get, renegotiation bit clearing, loopback modes, downshift programming, WoL wake on magic/link, stable stats under traffic, temperature reads, firmware version reporting, and ART capability retrieval.
