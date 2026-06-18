# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f11.c

## Purpose

`rmi_f11.c` implements RMI4 Function 11, the legacy 2-D touch sensor function. It discovers the sensor register layout from F11 query registers, configures a shared `rmi_2d_sensor`, reads absolute or relative touch packets on attention interrupts, and reports multitouch events through the Linux input subsystem.

## Important APIs, Types, and Functions

`struct f11_2d_sensor_queries` is the parsed capability model for F11 query registers. `struct f11_2d_ctrl` stores the base control block. `struct f11_2d_data` holds pointers into the allocated packet buffer, and `struct f11_data` combines query flags, control state, IRQ masks, platform data, and the embedded `rmi_2d_sensor`. Important functions include `rmi_f11_get_query_parameters()`, `f11_2d_construct_data()`, `rmi_f11_initialize()`, `rmi_f11_finger_handler()`, `rmi_f11_attention()`, `rmi_f11_config()`, and `rmi_f11_resume()`.

## Control Flow

Probe calls `rmi_f11_initialize()`, then configures the input device through `rmi_2d_sensor_configure_input()`. Initialization reads query0, parses the variable-length per-sensor query stream, reads control registers, derives physical dimensions and max X/Y, builds packet offsets, allocates tracking/object arrays, applies platform overrides, and writes control registers back. Config toggles the absolute and relative IRQ masks separately. Attention reads either the transport-provided attention bytes or the F11 data registers, then parses finger states, absolute positions, relative deltas, optional kernel tracking, and reports an input MT frame. Resume optionally waits and issues the F11 rezero command.

## State and Persistence Behavior

The driver persists query-derived packet layout, control register shadow bytes, input tracking arrays, and IRQ masks in `f11_data`. Device state is changed by writing F11 control registers for report mode, threshold, dribble, and palm-detect settings. Runtime touch objects are ephemeral per packet. The rezero delay is persistent platform/device configuration used after resume.

## Dependencies and Integration Points

The file depends on RMI core reads/writes, OF or platform `rmi_2d_sensor_platform_data`, the shared `rmi_2d_sensor` helper layer, Linux input MT helpers, and RMI IRQ mask management. It consumes transport attention buffers through `rmi_driver_data.attn_data`.

## Risks and Edge Cases

F11 has many optional query-dependent registers, so offset accounting is the key correctness risk. Partial attention reports are processed by reducing the valid byte count, which can produce fewer fingers than expected. The code reports invalid reserved finger states but continues. The config path writes `dev_controls` to `fn->fd.query_base_addr` instead of the control base address, which is suspicious and should be regression-tested against real hardware. Gesture fields are laid out but mostly not reported. Devices with unusual optional queries may expose layout combinations this driver does not fully understand.

## Test Signals

Test signals include absolute and relative F11 devices, query combinations with gestures, touch shapes, jitter, physical properties, ACM, and info2, platform axis alignment and threshold overrides, kernel tracking on/off, reduced attention packet sizes, resume rezero behavior, IRQ mask changes, and register-write verification for control configuration.
