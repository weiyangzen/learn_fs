# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-isys.c

## Purpose
This file adapts the generic fw-com layer to the IPU6 input-system firmware ABI. It configures ISYS queue topology, starts/stops the SP cell, sends stream/proxy commands, receives firmware responses, and provides debug dumps for stream configuration and frame buffer sets.

## Important APIs, types, and functions
`ipu6_fw_isys_init()` configures fw-com queues and opens communication. `ipu6_isys_fwcom_cfg_init()` builds proxy, device, and per-stream message queue sizes plus SRAM partitioning. `start_sp()` and `query_sp()` control the ISYS SP status register. `ipu6_fw_isys_complex_cmd()` and `ipu6_fw_isys_simple_cmd()` send stream commands. `ipu6_fw_isys_send_proxy_token()` sends proxy MMIO writes and polls `handle_proxy_response()`. `ipu6_fw_isys_close()` and `ipu6_fw_isys_cleanup()` close/release fw-com. `ipu6_fw_isys_get_resp()` and `ipu6_fw_isys_put_resp()` wrap receive-token access. Dump helpers log stream config and frame-buffer payloads.

## Control flow and integration points
On ISYS runtime bring-up, queue counts are derived from requested streams and hardware maximums, then passed to `ipu6_fw_com_prepare()` with ISYS-specific config. `ipu6_fw_com_open()` starts SP, and the code polls for READY. Stream open/start/capture/stop/flush/close commands are sent by placing payload DMA addresses into per-stream send queues. Proxy writes use the proxy send queue and wait for a matching request ID on the proxy response queue.

## State, persistence, and dependencies
State is `isys->fwcom`, protected during close by `isys->power_lock`, plus devm-allocated queue config and ISYS firmware config. The code depends on fw-com, IPU6 ISYS platform data, SP status registers, firmware ABI types, cache flushing for command payloads, and ISYS stream management code in other files.

## Risks and test signals
Risks are queue-count mismatch with firmware, failure to release fw-com after open errors, stale payload cache before commands, proxy response ID mismatches, command queue full returns, and close races with IRQ handlers. Test signals include ISYS firmware READY, stream open/start/capture responses, proxy writes completing, command timeout handling, clean runtime suspend close/reopen, and debug dumps matching configured pins/buffers.
