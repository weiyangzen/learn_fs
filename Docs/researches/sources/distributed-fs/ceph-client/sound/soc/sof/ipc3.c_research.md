<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c

## Purpose
Core IPC3 implementation for SOF. It logs and sends IPC3 messages, waits for replies, handles oversized control payload chunking, parses firmware-ready mailbox data, dispatches inbound notifications, implements IPC3 PM messages, and aggregates IPC3 ops.

## Important APIs, Types, and Functions
Important functions include `ipc3_log_header()`, `sof_ipc3_get_reply()`, `ipc3_wait_tx_done()`, `ipc3_tx_msg_unlocked()`, `sof_ipc3_tx_msg()`, `sof_ipc3_set_get_data()`, `sof_ipc3_get_ext_windows()`, `sof_ipc3_get_cc_info()`, `ipc3_fw_parse_ext_data()`, `ipc3_get_windows()`, `sof_ipc3_validate_fw_version()`, `ipc3_fw_ready()`, stream handlers `ipc3_period_elapsed()` and `ipc3_xrun()`, message dispatchers `ipc3_stream_message()`, `ipc3_comp_notification()`, `ipc3_trace_message()`, exported `sof_ipc3_do_rx_work()`, `sof_ipc3_rx_msg()`, and PM helpers for core state, context save/restore, and PM gate. `ipc3_ops` aggregates topology, PM, PCM, loader, dtrace, TX/RX, data transfer, and reply operations.

## Control Flow, State, and Persistence
TX paths optionally resume DSP to D0, serialize on `ipc->tx_mutex`, install shared message state via generic `sof_ipc_send_msg()`, wait on the message waitqueue, copy replies, and handle timeout as firmware exception. Large control data is split into chunks no larger than `ipc->max_payload_size`, with `msg_index`, `num_elems`, and `elems_remaining` tracking progress. Firmware-ready handling reads the ready struct from SRAM on first boot, validates ABI, parses extended data, sets inbox/outbox/stream/debug mailbox regions, adds debugfs windows, and allocates the reply buffer. RX reads headers/messages from the outbox, validates size, dispatches FW_READY, component control notifications, stream positions/XRUNs, trace DMA positions, and client IPC notifications. PM helpers send IPC3 context/core/gate commands.

## Dependencies and Integration
Depends on SOF IPC/control/stream UAPI headers, trace events, IPC3 topology/control/PCM/loader/dtrace ops, SOF mailbox/window/block IO, ALSA PCM/compress notifications, client IPC dispatcher, and platform send/mailbox callbacks. It is selected by `snd_sof_ipc_init()` for `SOF_IPC_TYPE_3`.

## Risks and Test Signals
Risks include IPC timeout recovery correctness, reply-size validation, chunked control offset arithmetic, firmware-ready extended data bounds, mailbox window mismatch between manifest and firmware, and inbound message size validation. Test signals are IPC flood and timeout tests, firmware ABI strict/non-strict compatibility, FW_READY with manifest and mailbox windows, stream period/XRUN notifications, control notifications, trace DMA position updates, core enable/disable IPCs, context save/restore, PM gate IPC in low-power states, and debug payload dump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc3.c -->
