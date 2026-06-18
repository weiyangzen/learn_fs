# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_isys_abi.h

## Purpose

This packed ABI header defines the IPU7 ISYS firmware command/response protocol: queue layout, stream open/capture/close commands, MIPI identifiers, frame formats, stream and frame message maps, stream configuration, buffer sets, responses, send tokens, and error codes.

## Important APIs, Types, and Functions

Important constants define output queues, input queues, stream limit, output pin limit, and queue IDs. Enums define response types, send types, MIPI VC/port values, frame formats, DPCM, output destinations, and token flags. Main packed structs are `ipu7_insys_resolution`, `ipu7_insys_capture_output_pin_payload`, `ipu7_insys_output_link`, `ipu7_insys_output_pin`, `ipu7_insys_input_pin`, `ipu7_insys_stream_cfg`, `ipu7_insys_buffset`, `ipu7_insys_resp`, `ipu7_insys_resp_queue_token`, and `ipu7_insys_send_queue_token`.

## Control Flow

The ABI is used by `ipu7-fw-isys.c` and video code: stream configuration buffers are sent with `STREAM_OPEN`, buffer sets are sent with start/capture commands, firmware writes response tokens to output queues, and host code consumes responses from syscom.

## State and Persistence Behavior

State is queue-token and payload memory shared by host and firmware. Stream IDs, frame IDs, user tokens, DMA addresses, and error records tie firmware responses back to V4L2 streams and buffers.

## Dependencies and Integration Points

It includes common ABI and is used by ISYS video/queue/CSI code. It depends on syscom queue sizing and boot configuration from the base module.

## Risks and Edge Cases

The file self-includes its own guard path, which is harmless due to include guards but unusual. Packed layout and queue IDs are firmware ABI. Max stream, input pin, output pin, and frame format limits must match video code. Error groups distinguish general, stream, and capture failures.

## Test Signals

Test stream open/start/capture/flush/abort/close, response parsing for SOF/EOF/pin-ready, all supported raw/YUV formats, stream ID bounds, and firmware error propagation.
