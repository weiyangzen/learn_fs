# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.h

## Purpose
This header defines board-description structures and hardware flag constants used by the cx18 driver to adapt one PCI core to many capture-card layouts.

## Important APIs, Types, and Functions
Hardware flags include `CX18_HW_TUNER`, `CX18_HW_TVEEPROM`, `CX18_HW_CS5345`, `CX18_HW_DVB`, `CX18_HW_418_AV`, `CX18_HW_GPIO_MUX`, `CX18_HW_GPIO_RESET_CTRL`, and `CX18_HW_Z8F0811_IR_HAUP`. Types include `cx18_card_video_input`, `cx18_card_audio_input`, `cx18_card_pci_info`, GPIO init/reset/audio descriptors, tuner descriptors, tuner I2C address tables, `cx18_ddr`, and the aggregate `struct cx18_card`. Public prototypes are `cx18_get_input()`, `cx18_get_audio_input()`, and `cx18_get_card()`.

## Control Flow
The header has no executable flow. It defines the contract consumed by card tables, PCI probe, subdevice registration, V4L2 input enumeration, GPIO reset/mux code, I2C probing, and DDR initialization.

## State and Persistence
`struct cx18_card` instances are static configuration. Their data is copied or referenced by `struct cx18` at probe time and remains the source of truth for board capabilities until device removal.

## Dependencies and Integration Points
It depends on V4L2 capability and standard identifiers plus tuner IDs. It is an integration point between `cx18-cards.c`, `cx18-driver.c`, `cx18-gpio.c`, `cx18-i2c.c`, `cx18-firmware.c`, `cx18-dvb.c`, and ioctl input/audio handling.

## Risks and Edge Cases
Array size constants cap the number of inputs and tuners; adding a board with more routes requires structure changes. Hardware flags are bit positions that must stay aligned with arrays in `cx18-i2c.c`. GPIO masks assume no overlap between active-low and active-high reset lines.

## Test Signals
Compile-time signals include all board initializers matching structure fields and no out-of-range array use. Runtime signals include correct `VIDIOC_ENUMINPUT`, `VIDIOC_ENUMAUDIO`, subdevice creation, reset behavior, and firmware DDR stability per card.
