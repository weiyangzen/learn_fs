## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Kconfig

### Purpose
`Kconfig` defines build options for the Philips/OEM USB webcam driver.

### Important APIs, Types, And Functions
The main symbol is `USB_PWC`, a tristate depending on `VIDEO_DEV` and selecting `VIDEOBUF2_VMALLOC`. Optional symbols are `USB_PWC_DEBUG` for verbose driver traces and `USB_PWC_INPUT_EVDEV` for snapshot-button input event support.

### Control Flow
Kconfig has no runtime flow, but it controls which code paths compile. `USB_PWC_INPUT_EVDEV` defaults to `y` when input support is compatible, and the C sources conditionally include input-device and debug code.

### State, Persistence, And Dependencies
Build configuration persists in the kernel `.config`. The selected symbols affect module contents, module parameters, debug logging, and whether an input device is registered for the camera button.

### Integration Points
The configuration integrates this driver with the media USB webcam menu, V4L2 core, videobuf2 vmalloc memory backend, and optional Linux input subsystem.

### Risks
The dependency expression for input support must remain aligned with Kconfig symbol semantics for `INPUT` and modular builds. Missing `VIDEOBUF2_VMALLOC` selection would break the vb2 queue used by `pwc-if.c`.

### Test Signals
Configuration tests should build `USB_PWC=y`, `USB_PWC=m`, debug on/off, input-event support on/off, and combinations where input is modular or disabled.
