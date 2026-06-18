# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.h

This header defines the firmware-to-host HFI message ABI used by the Qualcomm Venus driver. It is not executable logic; its purpose is to give `hfi_msgs.c` and the Venus transport a typed view of system messages, session completions, event notifications, fill-buffer-done packets, debug strings, and coverage records returned through the HFI message queue.

Important API elements are the `HFI_MSG_*` packet type constants, picture/frame flag constants, and packet structs such as `hfi_msg_sys_init_done_pkt`, `hfi_msg_event_notify_pkt`, `hfi_msg_session_empty_buffer_done_pkt`, `hfi_msg_session_fbd_compressed_pkt`, and `hfi_msg_session_fbd_uncompressed_plane0_pkt`. The header also declares `hfi_process_watchdog_timeout()` and `hfi_process_msg_packet()`, which are the integration points consumed by `hfi_venus.c` after reading messages from firmware.

Control flow is indirect: `venus_isr_thread()` drains the message queue, passes each packet header to `hfi_process_msg_packet()`, and branches on the returned message code for system init/resource/power-collapse handling. The flexible array members in many structs model variable-sized property payloads and multi-plane buffer metadata, so packet size validation in the queue reader is critical.

State and persistence are limited to wire data. Firmware state is reflected through packet fields such as `error_type`, `event_id`, `filled_len`, timestamps, picture type, output tags, and buffer addresses. The structs depend on lower-level packet headers from `hfi_helper.h`/`hfi.h` and Linux fixed-width types.

Risks center on ABI drift and bounds. Any field layout change can corrupt message parsing, buffer completion, or event handling. Flexible arrays require callers to validate packet size before dereferencing. Test signals include successful firmware init, session start/stop acknowledgements, fill-buffer-done delivery for compressed and raw paths, EOS/source-change events, and watchdog/system-error reporting.
