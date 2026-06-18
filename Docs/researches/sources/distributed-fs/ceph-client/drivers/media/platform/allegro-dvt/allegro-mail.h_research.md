# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.h

## Purpose

`allegro-mail.h` defines the C representation of the Allegro firmware mailbox protocol. It provides message type/version enums, request and response structs, create-channel parameter layout, encode options, response unions, and serializer/parser prototypes.

## Important APIs, Types, And Symbols

- `enum mcu_msg_type` defines protocol commands such as `INIT`, `CREATE_CHANNEL`, `DESTROY_CHANNEL`, `ENCODE_FRAME`, `PUT_STREAM_BUFFER`, and internal buffer push commands.
- `enum mcu_msg_version` distinguishes `MCU_MSG_VERSION_2018_2` and `MCU_MSG_VERSION_2019_2`.
- `struct create_channel_param` is the large channel configuration contract covering format, codec profile/level/tier, reference counts, loop filters, motion estimation ranges, rate control, GOP settings, LDA factors, and merge candidates.
- Request structs include `mcu_msg_init_request`, `mcu_msg_create_channel`, `mcu_msg_destroy_channel`, `mcu_msg_push_buffers_internal`, `mcu_msg_put_stream_buffer`, and `mcu_msg_encode_frame`.
- Response structs include `mcu_msg_init_response`, `mcu_msg_create_channel_response`, `mcu_msg_destroy_channel_response`, and `mcu_msg_encode_frame_response`.
- `union mcu_msg_response` lets the core allocate one response object and dispatch based on `header.type`.
- Option bits include `AL_OPT_FORCE_LOAD`, `AL_OPT_USE_L2`, `AL_OPT_UPDATE_PARAMS`, and related encode/request flags.

## Control Flow

This header has no executable flow, but it defines the structures consumed by the flow in `allegro-core.c` and serialized by `allegro-mail.c`. The flexible array member in `mcu_msg_push_buffers_internal` lets the core create variable-length internal buffer lists for the firmware.

## State And Persistence

The structs represent transient mailbox messages and channel creation state. They are not persisted outside memory or firmware mailboxes. Handles in stream/frame messages persist only long enough for a firmware response to identify the matching vb2 buffers.

## Dependencies And Integration Points

The header depends on kernel integer types and `BIT()` from `<linux/kernel.h>`. It integrates tightly with the core driver's `fill_create_channel_param()` and mailbox send/receive code. The response fields are also consumed by NAL generation, especially HEVC tile layout in `mcu_msg_encode_frame_response`.

## Risks

This is an ABI-like contract with firmware; field reordering or type-size changes can silently break hardware communication. The counted flexible array relies on correct `struct_size()` allocation by callers. Several fields are reserved or unknown, so readers should avoid assuming they are free for reuse.

## Test Signals

Build warnings around flexible arrays or struct types are useful early signals. Runtime tests should verify create-channel and encode-frame responses are decoded with expected ids, buffer counts, error codes, and tile metadata for each supported firmware version.
