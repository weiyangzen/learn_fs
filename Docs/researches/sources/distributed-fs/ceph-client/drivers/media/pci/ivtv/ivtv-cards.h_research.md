# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.h

## Purpose
`ivtv-cards.h` defines the card descriptor contract used by ivtv probe, routing, GPIO, I2C, and ioctl enumeration code. It assigns stable card indices, PCI vendor/device constants, hardware capability bits, logical input/output identifiers, and the structures used by `ivtv-cards.c`.

## Important APIs, Types, and Functions
Important definitions include `IVTV_CARD_*` card IDs, `IVTV_HW_*` bitmasks, input constants such as `IVTV_CARD_INPUT_VID_TUNER`, V4L2 capability aliases `IVTV_CAP_ENCODER` and `IVTV_CAP_DECODER`, and descriptor structs `ivtv_card`, `ivtv_card_video_input`, `ivtv_card_audio_input`, `ivtv_card_output`, `ivtv_card_pci_info`, GPIO helper structs, and tuner I2C structs. It declares the card/input/output query functions implemented in `ivtv-cards.c`.

## Control Flow
The header is declarative, but it constrains runtime control flow by requiring hardware bit positions to remain gapless and descriptor arrays to use sentinel zero entries. Card variant IDs are placed after `IVTV_CARD_LAST` so probe can use user-visible card numbers for normal cards while still supporting refined internal variants.

## State and Persistence
No mutable state lives here. Constants define how `struct ivtv` caches card identity, subdevice masks, tuner tables, and GPIO behavior at runtime.

## Dependencies and Integration Points
The header depends on V4L2 types and tuner IDs pulled indirectly through `ivtv-driver.h`. It integrates with the I2C hardware arrays in `ivtv-i2c.c`, GPIO setup in `ivtv-gpio.c`, stream capability decisions in `ivtv-driver.c`, and V4L2 input/output ioctl helpers.

## Risks and Edge Cases
The `IVTV_HW_BIT_*` enum explicitly disallows gaps because bit numbers index parallel arrays in `ivtv-i2c.c`; adding or reordering bits without updating those arrays breaks subdevice registration. Card index changes affect module parameter cardtype numbering. Descriptor array limits cap cards at six video inputs, three audio inputs, and three tuner choices.

## Test Signals
Compile-time coverage should catch missing struct fields, but functional tests should validate new hardware bits against I2C arrays, cardtype module parameter numbering, input enumeration bounds, and probe behavior for both standard card IDs and post-`IVTV_CARD_LAST` variants.
