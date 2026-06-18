# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f12.c

## Purpose

`rmi_f12.c` implements RMI4 Function 12, the newer 2-D touch sensor interface. Unlike F11, F12 uses register descriptors to describe query, control, and data registers, then reports sensed objects from Data1 packets through the shared RMI 2-D sensor/input path.

## Important APIs, Types, and Functions

`enum rmi_f12_object_type` maps F12 object classifications to internal object types and MT tools. `struct f12_data` stores the embedded `rmi_2d_sensor`, platform data, register descriptors, offsets for selected Data registers, and absolute/relative IRQ masks. Important functions are `rmi_f12_read_sensor_tuning()`, `rmi_f12_process_objects()`, `rmi_f12_attention()`, `rmi_f12_write_control_regs()`, `rmi_f12_config()`, and `rmi_f12_probe()`.

## Control Flow

Probe verifies that register descriptors are present, allocates `f12_data` plus IRQ masks, reads the query/control/data descriptors, computes full data packet size, reads sensor tuning from Control8, and walks Data0 through Data15 to decide which registers are present in direct reads or HID attention reports. Data1 enables absolute reporting and sets the number of tracked objects. Tracking buffers and object arrays are allocated before `rmi_2d_sensor_configure_input()`. Config enables the absolute IRQ mask when needed, clears relative IRQs, and optionally writes the dribble bit in Control20. Attention copies transport attention bytes or reads the data registers, processes Data1 object records, and syncs the MT frame.

## State and Persistence Behavior

F12 stores descriptor-derived offsets and sizes, selected input mode, sensor dimensions, and object/tracking arrays. It persists only a small control mutation for dribble state; touch object state is rebuilt per report. `sensor->attn_size` may be smaller than full packet size when HID attention reports omit unreported descriptors.

## Dependencies and Integration Points

The file depends on RMI register descriptor helpers, RMI transport reads/writes, `rmi_2d_sensor`, Linux input MT, OF/platform sensor properties, and the shared RMI attention-data buffer. It is the main integration path for modern Synaptics RMI touchpads/touchscreens that expose Function 12.

## Risks and Edge Cases

Descriptor parsing must match the device's reported subpacket layout. `rmi_f12_process_objects()` checks available size for Data1, but uses the overall valid byte count rather than bytes remaining from `data1_offset`, which can overestimate available object bytes if preceding data is present. Relative Data9 is discovered but not reported in the attention path. The DPM resolution path divides by the read value without an explicit zero check. Dribble control assumes the enable bit is within the first three bytes of Control20.

## Test Signals

Coverage should include descriptor-present and descriptor-missing devices, HID attention versus register-read data paths, Data1 object classification for finger/stylus/palm/unclassified, truncated attention reports, Control8 tuning with DPM and pitch/receiver fallbacks, dribble on/off/default settings, and V4L/input event validation for touchscreen and touchpad platform settings.
