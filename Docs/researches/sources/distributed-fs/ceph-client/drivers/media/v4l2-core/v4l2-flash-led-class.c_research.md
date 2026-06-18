# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-flash-led-class.c

## Purpose
`v4l2-flash-led-class.c` bridges Linux LED flash-class devices into V4L2 flash subdevices. It maps LED brightness, timeout, strobe, fault, torch, flash, indicator, and external-strobe operations to V4L2 controls and registers a V4L2 subdevice with a media entity and devnode.

## Important APIs, Types, and Functions
Public APIs are `v4l2_flash_init`, `v4l2_flash_indicator_init`, and `v4l2_flash_release`. Important internal functions include `v4l2_flash_g_volatile_ctrl`, `v4l2_flash_s_ctrl`, `v4l2_flash_init_controls`, `__sync_device_with_v4l2_controls`, `v4l2_flash_open`, `v4l2_flash_close`, and `__v4l2_flash_init`. Core state lives in `struct v4l2_flash`: LED classdev pointers, V4L2 subdev, control handler, control pointer array, and optional conversion/external-strobe ops.

## Control Flow
Initialization allocates `struct v4l2_flash`, fills LED and operation pointers, initializes a V4L2 subdevice with internal open/close ops and `V4L2_SUBDEV_FL_HAS_DEVNODE`, sets the media entity function to `MEDIA_ENT_F_FLASH`, initializes controls based on LED capabilities and `v4l2_flash_config`, takes an fwnode reference, and async-registers the subdevice. Indicator-only initialization calls the same shared path with only an indicator LED.

Control setup builds `v4l2_ctrl_config` entries from LED flash settings. It conditionally creates controls for LED mode, torch intensity, flash intensity, indicator intensity, flash timeout, strobe source, strobe, strobe stop, strobe status, and fault. The control ops route reads of volatile controls to LED update/get APIs and writes to LED brightness, flash brightness, timeout, strobe, and optional external-strobe callbacks. LED mode transitions stop active strobe, turn torch off when entering flash mode, enable torch brightness when entering torch mode, and cache strobe source until flash mode when needed.

Open and close are tied to `v4l2_fh_is_singular`: on first V4L2 open, LED sysfs access and triggers are disabled for the flash/indicator LEDs and device state is synchronized from V4L2 controls; on last close, sysfs access is re-enabled and strobe source is reset to software when present. Release unregisters the async subdevice, drops fwnode reference, frees controls, and cleans the media entity.

## State and Persistence Behavior
State persists in the control handler and LED class devices while the subdevice is registered. V4L2 control values cache desired torch intensity, flash intensity, timeout, LED mode, and strobe source. Hardware state is synchronized on first open and on relevant control writes. No on-disk persistence is involved; sysfs availability is temporarily changed while V4L2 owns the LED.

## Dependencies and Integration Points
The file depends on LED class/flash APIs, V4L2 controls, V4L2 async subdevice registration, media entity setup, fwnode references, and V4L2 file-handle singular-open detection. It is used by LED flash drivers that want V4L2 camera flash integration.

## Risks
Conversion between microamp intensity and LED brightness must honor min/step and indicator LED zero semantics. External-strobe mode is optional and has hardware-specific side effects. Open failure after sysfs disable must re-enable sysfs for both LEDs. Missing or mismatched LED capabilities produce limited controls. First-open/last-close behavior depends on correct file-handle lifecycle. Fault and strobe status are volatile and can fail at read time.

## Test Signals
Test control creation for flash-only, indicator-only, and combined devices; brightness/intensity conversion at min, max, and step boundaries; LED mode transitions; software strobe busy checks; external strobe source callbacks; volatile fault/status reads; open/close sysfs disable/enable; async registration failure unwind; and release idempotence for NULL/error pointers.
