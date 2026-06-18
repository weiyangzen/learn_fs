# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-gpio.c

## Purpose
`ivtv-gpio.c` implements GPIO-backed board controls as a V4L2 subdevice. It initializes card-specific GPIO direction/output values and exposes GPIO routing, audio mute, tuner mode, audio clock, and reset hooks for cards whose muxes or tuners are wired to CX2341x GPIO pins.

## Important APIs, Types, and Functions
Public functions are `ivtv_gpio_init()`, `ivtv_reset_ir_gpio()`, and `ivtv_reset_tuner_gpio()`. Internal subdev callbacks include `subdev_s_clock_freq()`, `subdev_g_tuner()`, `subdev_s_tuner()`, `subdev_s_radio()`, `subdev_s_audio_routing()`, `subdev_s_ctrl()`, `subdev_log_status()`, and `subdev_s_video_routing()`.

## Control Flow
Probe calls `ivtv_gpio_init()` after MMIO mapping. If the card has GPIO init data or an Xceive reset pin, the function writes initial output and direction registers, initializes `itv->sd_gpio`, creates an audio mute control, runs control setup, and registers the subdevice. Later V4L2 routing and tuner callbacks read masks and values from the active card descriptor and update only the relevant GPIO output bits. Reset helpers pulse fixed PVR-150 IR lines or a card-specific Xceive tuner pin.

## State and Persistence
Runtime state is in hardware GPIO registers and the GPIO V4L2 control handler. Descriptor masks and values are static. Register state is volatile and reinitialized on probe.

## Dependencies and Integration Points
The file depends on card descriptors, V4L2 subdev/control APIs, tuner and xc2028 reset interfaces, and ivtv MMIO macros. Routing code in `ivtv-routing.c`, tuner setup, radio switching, and control handlers call into this GPIO subdevice through standard V4L2 subdev operations.

## Risks and Edge Cases
Wrong GPIO masks can mute audio, select the wrong input, hold a tuner in reset, or fail to reset IR hardware. GPIO register updates are read-modify-write without a local lock, so callers rely on higher-level serialization. `subdev_g_tuner()` treats absent detect masks as full stereo/language capability.

## Test Signals
Validate initial GPIO DIR/OUT logs, mute control behavior, tuner/composite/S-Video routing, radio audio routing, audio sample frequency pin changes, detected mono/stereo reporting on supported boards, PVR-150 IR reset, Xceive tuner reset, and subdev log-status output.
