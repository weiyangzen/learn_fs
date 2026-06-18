# sources/distributed-fs/ceph-client/include/media/davinci/vpif_types.h

Purpose: Platform-data structures for TI DaVinci VPIF capture/display channels, subdevices, routing, and per-board callbacks.

Important APIs/types/functions: Defines channel maxima, `enum vpif_if_type`, `vpif_interface`, `vpif_subdev_info`, `vpif_output`, display channel/config structs, `vpif_input`, capture channel/config structs, and callback hooks such as `set_clock`, `setup_input_channel_mode`, and `setup_input_path`.

Control flow: Board data enumerates I2C subdevices, input/output routes, interface polarities, channel capabilities, and async subdevice connections. Capture/display drivers consume these tables during probe and when userspace selects inputs or outputs.

State and persistence: No internal runtime state. The structures persist as platform data owned by the board or platform driver.

Dependencies and integration: Depends on I2C board info, V4L2 input/output types, and V4L2 async connection pointers. Integrates VPIF with sensor/decoder/encoder subdevices.

Risks and test signals: Risks include mismatched routes, invalid I2C adapter IDs, incorrect async connection sizes, and board callbacks failing. Test multi-channel capture/display, input/output switching, clock programming, and async probe/unbind behavior.
