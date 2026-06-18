<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h

## Purpose
`smscoreapi.h` is the public contract for the Siano core. It declares firmware names, device families, device modes, protocol message ids, message wire structures, statistics structures, GPIO configuration structures, callback typedefs, and exported APIs used by Siano transports and DVB/IR clients.

## Important APIs, Types, and Functions
Key public types include `smscore_device_t`, `smscore_client_t`, `smscore_buffer_t`, `smsdevice_params_t`, `smsclient_params_t`, `sms_msg_hdr`, `sms_msg_data`, `sms_data_download`, `sms_version_res`, `sms_firmware`, `sms_stats`, `sms_isdbt_stats`, `sms_isdbt_stats_ex`, DVB RX/TX statistics structures, and `smscore_config_gpio`.

The header defines callback typedefs for hotplug, mode switching, transport send, firmware preload/postload, response handling, and removal. It exports core lifecycle APIs, client APIs, message send/receive hooks, buffer pool APIs, GPIO APIs, board id helpers, LED state, and message translation.

## Control Flow
The header models a layered driver: a transport fills `smsdevice_params_t`, receives a `smscore_device_t`, and exposes transport-specific send/mode/preload callbacks. Higher-level protocol clients register `smsclient_params_t` callbacks with an initial message id and data type, then send Siano protocol messages through `smsclient_sendrequest()`. Incoming buffers are delivered to `smscore_onresponse()` and routed back by message type/destination id.

## State and Persistence Behavior
`struct smscore_device_t` is the main in-memory state container. It stores lists of clients and buffers, common DMA memory metadata, transport context, devpath, mode, supported modes, all request completions, GPIO result state, board id, firmware metadata, IR state, LED state, and optional media-controller device pointer. No disk persistence is defined; the implementation keeps module-lifetime registry state by devpath.

## Dependencies and Integration Points
The header integrates Linux device/list/mutex/wait/timer/scatterlist primitives, media-device support, page alignment, and `smsir.h`. Its firmware names must match `smscoreapi.c` module firmware declarations and board-specific firmware tables in `sms-cards`. The message id enum is shared with firmware and therefore has ABI-like constraints.

## Risks and Test Signals
Because this header defines protocol wire layouts, padding, field size, and endian assumptions are critical. Changes to `enum msg_types`, `sms_msg_hdr`, or statistics structures can break firmware communication and DVB statistics parsing. The `SMS_PROTOCOL_MAX_RAOUNDTRIP_MS` spelling is preserved in code and should not be casually renamed without updating all users.

Test signals include compile coverage across `CONFIG_MEDIA_CONTROLLER_DVB`, `CONFIG_SMS_SIANO_RC`, and `CONFIG_SMS_SIANO_DEBUGFS`, successful structure use by `smscoreapi.c` and `smsdvb-main.c`, and compatibility with big-endian conversion helpers in `smsendian.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h -->
