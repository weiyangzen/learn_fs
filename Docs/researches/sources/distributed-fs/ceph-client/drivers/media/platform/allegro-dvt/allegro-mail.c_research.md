# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.c

## Purpose

`allegro-mail.c` translates between the driver's typed C mailbox message structs and the 32-bit word protocol used by Allegro firmware. It hides firmware-version differences, packs bitfields for requests, unpacks firmware responses, and supplies message type names for logging.

## Important APIs, Types, And Functions

- `msg_type_name()` maps `enum mcu_msg_type` values to human-readable names and formats unknown values.
- `allegro_encode_mail()` is the main request serializer. It dispatches to per-message encoders and writes a combined type/body-length header word.
- `allegro_decode_mail()` is the main response parser. It reads the type from the mailbox header and fills `union mcu_msg_response` members.
- `allegro_encode_config_blob()` serializes `struct create_channel_param` into the firmware create-channel configuration blob, with branches for `MCU_MSG_VERSION_2018_2` and `MCU_MSG_VERSION_2019_2`.
- `allegro_decode_config_blob()` extracts reference-index values that changed location between firmware versions.
- Internal encoders handle init, create/destroy channel, push internal buffers, put stream buffer, and encode-frame requests.
- Internal decoders handle init, create-channel, destroy-channel, and encode-frame responses.

## Control Flow

Request flow starts with a typed message whose first field is `struct mcu_msg_header`. `allegro_encode_mail()` dispatches on `header.type`, writes the body into `dst[1...]`, and writes the firmware header to `dst[0]` with the high 16 bits as type and low 16 bits as byte length. For create-channel requests, older firmware embeds the whole config blob in the message, while 2019.2+ firmware receives a DMA-visible blob address.

Response flow starts with `allegro_decode_mail()`, which extracts the response type from `src[0]`, advances past the header, and dispatches to a decoder. The encode-frame response parser reconstructs 64-bit handles, extracts packed fields such as skip/reference flags, tile dimensions, QP, slice type, and IDR flags, and optionally consumes 2019.2 reserved words.

## State And Persistence

The file does not keep persistent state. All state is passed in message structs and word buffers. The only static mutable object is the fallback buffer in `msg_type_name()` for formatting unknown message ids; concurrent callers can overwrite that string.

## Dependencies And Integration Points

It depends on Linux bitfield helpers, errno, string helpers, V4L2 pixel format constants, and the protocol definitions in `allegro-mail.h`. It is called by `allegro-core.c` before writing command mailboxes and after reading status mailboxes. Firmware-version conditionals must remain aligned with `supported_firmware[]` in the core driver.

## Risks

Protocol layout mistakes are high impact because firmware will misinterpret requests or the driver will mis-handle returned buffers. Some bit packing uses signed values through `FIELD_PREP`, so range and sign-extension assumptions matter. The config blob has many partly documented or unknown fields, making regression risk high when changing encoder parameters. `msg_type_name()`'s static buffer is not thread-safe for unknown types, though logging impact is minor.

## Test Signals

Good tests include round-trip encode/decode fixtures for known firmware versions, byte-for-byte comparison against known working firmware messages, compile coverage for both protocol versions, and runtime traces confirming create-channel responses allocate the expected internal/reference buffer counts. Encode-frame response tests should validate 64-bit handle reconstruction and partition/tile fields.
