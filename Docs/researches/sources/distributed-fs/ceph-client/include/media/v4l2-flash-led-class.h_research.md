# sources/distributed-fs/ceph-client/include/media/v4l2-flash-led-class.h

Purpose: declares helpers that wrap Linux LED flash/indicator class devices as V4L2 subdevices with V4L2 controls and media-entity naming.

Important APIs/types: `struct v4l2_flash_ctrl_data` pairs a `v4l2_ctrl_config` with the created control id. `struct v4l2_flash_ops` lets drivers configure external strobe and convert between V4L2 intensity units and LED brightness. `struct v4l2_flash_config` provides media entity name, intensity constraints, supported LED fault bitmask, and external-strobe capability. `struct v4l2_flash` stores LED class-device pointers, ops, embedded subdevice, control handler, and control pointer array. Inline container helpers convert from subdev or control to `v4l2_flash`.

Control flow: LED-backed camera drivers call `v4l2_flash_init()` for flash LEDs or `v4l2_flash_indicator_init()` for indicator LEDs. The framework builds controls from LED capabilities, initializes an embedded subdevice and control handler, and later `v4l2_flash_release()` tears it down. When `CONFIG_V4L2_FLASH_LED_CLASS` is disabled, init functions return NULL and release is a no-op.

State and persistence: flash state is in the allocated `v4l2_flash`, its control handler, and LED class device. The config is not retained after init returns, while `ops` is stored. Control values define the V4L2-visible flash state; LED subsystem state is the hardware-facing backend.

Dependencies and integration: includes `v4l2-ctrls.h` and `v4l2-subdev.h`, and depends on LED flash class types. It bridges media-controller subdevices, V4L2 controls, firmware node association, LED faults, torch/flash intensity, and external strobe wiring.

Risks: callers must handle NULL when the config option is disabled; config lifetime cannot be assumed after init; conversion callbacks must be monotonic and respect LED constraints; unsupported fault bits can mislead userspace; and control-to-flash container conversion assumes controls belong to `v4l2_flash.hdl`.

Test signals: init/release with flash and indicator devices, disabled-config stubs, external strobe enable/disable, intensity/brightness round trips, fault reporting controls, fwnode association, and control handler cleanup on init failures.
