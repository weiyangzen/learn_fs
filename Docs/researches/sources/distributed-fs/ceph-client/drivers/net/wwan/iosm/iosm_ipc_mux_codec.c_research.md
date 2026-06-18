# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.c

Purpose: encodes and decodes IOSM MUX Lite and aggregation wire formats. It sends mux commands, decodes command responses/flow-control/link-status tables, decodes DL datagrams, encodes UL datagrams into ADGH or ADBH/ADTH/QLTH blocks, manages UL credits/pending bytes, and recycles mux SKBs after CP consumes TDs.

Important functions: `ipc_mux_dl_decode`, `ipc_mux_dl_acb_send_cmds`, `ipc_mux_netif_tx_flowctrl`, `ipc_mux_ul_trigger_encode`, `ipc_mux_ul_data_encode`, `ipc_mux_ul_encoded_process`, `ipc_mux_ul_adb_finish`, and `ipc_mux_ul_adb_update_ql`.

Control flow: netdev TX queues SKBs into a session and schedules task-queue encode. Encoder round-robins sessions, respects flow masks, queue thresholds, byte watermarks, and credit limits, then queues mux SKBs on the IPC channel and starts TD update timers. DL decode switches on signatures for ADBH, ADGH, FCTH, ACBH, and CMDH, forwarding cloned packet payloads to WWAN or replying to commands. Blocking command sends wait on channel completion.

State/dependencies: uses `iosm_mux` sessions, transaction IDs, ACB/ADB scratch state, DMA SKB free lists, imem UL write/timers, task queue, WWAN RX/TX flow control, nospec bounds hardening, and PCIe SKB free. Risks: packet offset/length validation gaps, session index plus `wwan_q_offset` handling, underflow of pending bytes, flow-control deadlock, and blocking waits. Test signals: signature fuzzing, invalid if_id, FCT credit update, flow-control enable/disable ACKs, high/low watermark TX stop/restart, ADB size overflow, and SKB ownership on encode failures.
