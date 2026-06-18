# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c

## Purpose
`iris_hfi_gen2_packet.c` provides low-level Gen2 packet construction and V4L2-to-HFI color metadata packing. It hides the details of creating a Gen2 `iris_hfi_header` plus one or more `iris_hfi_packet` sub-packets.

## Important APIs, Types, And Functions
Color helpers map V4L2 colorspace, transfer function, and YCbCr encoding to HFI primaries/transfer/matrix values. `iris_hfi_gen2_get_color_info()` packs matrix, transfer, primaries, description-present, full-range, video-format, and signal-present bits. Packet helpers create headers and packets, and public builders emit system init, image-version query, session command, session property, IFPC property, and PC prep command.

## Control Flow
System init creates one header and eight sub-packets: `HFI_CMD_INIT` plus UBWC platform configuration properties. Image-version uses a get-property flag with no payload. Session command/property builders create one header and one packet in the instance's reusable buffer. Header and packet IDs are incremented from `core->header_id` and `core->packet_id`.

## State And Persistence Behavior
The functions mutate only caller-provided packet memory and increment core header/packet counters. UBWC values are read from immutable platform data. Generated packets are transient until written into the HFI command queue.

## Dependencies And Integration Points
It depends on Gen2 defines, common HFI host flags/payload enums, Gen2 instance wrapper, and platform UBWC configuration. Gen2 command ops call these helpers for all wire-format construction.

## Risks And Test Signals
There is no explicit buffer-size parameter in `iris_hfi_gen2_create_packet()`, so callers must allocate enough space. Tests should assert system init packet size equals expected constants, packet counters increment monotonically, payload bytes are copied correctly, and color-info bit packing round-trips with Gen2 response parsing.
