# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/cx231xx.h

## Purpose

`cx231xx.h` is the central internal interface for the Conexant cx231xx USB media driver. It collects board IDs, buffer and URB sizing, enums, common data structures, call macros, and function prototypes shared by analog video, VBI, audio, DVB, I2C, GPIO, AFE, DIF, core USB, board setup, and optional IR/MPEG extension code.

## Important APIs, Types, and Functions

Important constants include board IDs from `CX231XX_BOARD_UNKNOWN` through `CX231XX_BOARD_HAUPPAUGE_975`, queue defaults such as `CX231XX_MIN_BUF`, `CX231XX_NUM_BUFS`, `CX231XX_NUM_PACKETS`, VBI sizing, I2C addresses for internal blocks, and audio/stream bit flags.

Core enums describe mode (`CX231XX_SUSPEND`, `CX231XX_ANALOG_MODE`, `CX231XX_DIGITAL_MODE`), stream state, input type, video mux pins, audio mux, decoder presence, I2C master ports, device state, AFE mode, audio input, transfer type, and MPEG packet-header behavior.

Key structures include `cx231xx_isoc_ctl` and `cx231xx_bulk_ctl` for URB rings, `cx231xx_buffer` for vb2 buffers, `cx231xx_dmaqueue` for parser progress, `cx231xx_input` and `cx231xx_board` for board capabilities and routing, `cx231xx_audio`, `cx231xx_i2c`, `cx231xx_i2c_xfer_data`, `VENDOR_REQUEST_IN`, `cx231xx_tvnorm`, `cx231xx_video_mode`, `cx231xx_tsport`, and the main `struct cx231xx`.

Function prototypes cover every subsystem: I2C registration and data transfer, GPIO, AFE/I2S/DIF setup, video parsing, core USB control, URB initialization/teardown, mode and power control, stream start/stop, analog V4L2 registration/ioctls, board setup, extension registration, cx23417 MPEG support, and optional remote-control init/exit.

## Control Flow

The header defines cross-file call paths rather than executing them. Probe/board setup code fills `struct cx231xx`, registers I2C and V4L2 subdevices, and calls `cx231xx_register_analog_devices()` or DVB extension code depending on board capabilities. V4L2 streaming and DVB streaming then use the transfer structures and function pointers declared here. Subdevice calls are routed through `cx25840_call()`, `tuner_call()`, and `call_all()`.

## State and Persistence Behavior

`struct cx231xx` is the persistent in-kernel state for a device instance. It tracks model, board copy, USB device, V4L2 devices, subdevices, controls, tuner identity, current norm/frequency/input, dimensions, audio state, I2C buses and muxes, GPIO values, power mode, AFE state, active mode, VBI/sliced CC mode, transport stream ports, MPEG state, and work items. Parser state persists while streams run in `cx231xx_dmaqueue`. Hardware-derived EEPROM data is cached in `eedata[256]`.

## Dependencies and Integration Points

The header depends on Linux USB, I2C, V4L2, videobuf2, rc-core, cx2341x, and local register/config headers. It is included throughout the `cx231xx` driver and forms the dependency bridge between analog video files, VBI, audio, DVB, board tables, core USB, and AV/DIF configuration files. Because it declares optional inline stubs for IR, it also controls build behavior when `CONFIG_VIDEO_CX231XX_RC` is disabled.

## Risks

This is a high-blast-radius header: changes can rebuild or alter behavior across the entire driver. Layout changes to `struct cx231xx`, transfer controls, or parser queues can break assumptions in URB callbacks and teardown paths. Board flag semantics affect device registration and power/routing behavior. The main structure mixes lifetime domains including USB device, V4L2 objects, I2C clients, work items, and streaming buffers, so locking and ownership must be checked carefully for every field addition or user.

## Test Signals

Signals include all `cx231xx` translation units compiling under analog-only, DVB, audio, RC, media-controller, and advanced-debug configurations; successful probe/disconnect of supported board IDs; analog video, VBI, radio, DVB, audio, and IR smoke tests where available; and no sparse/coccinelle warnings around pointer ownership, missing prototypes, or structure-field type drift.
