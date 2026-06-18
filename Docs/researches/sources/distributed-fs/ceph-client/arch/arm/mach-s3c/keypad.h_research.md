<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h

### Purpose
Declares legacy platform-data hooks for Samsung keypad devices on S3C machines.

### Important APIs, Types, And Functions
`samsung_keypad_set_platdata(struct samsung_keypad_platdata *pd)` copies board keypad data into the platform device. `samsung_keypad_cfg_gpio(unsigned int rows, unsigned int cols)` is the architecture GPIO setup hook.

### Control Flow
Board files prepare a `samsung_keypad_platdata`, call `samsung_keypad_set_platdata()`, and the keypad driver later consumes the copied data. The GPIO callback is called during device setup.

### State, Persistence, And Dependencies
This header holds no state. It depends on `<linux/input/samsung-keypad.h>` for the platform data structure and on arch code providing the GPIO configuration function.

### Integration Points
`mach-crag6410.c` supplies keymaps and uses the setter. `setup-keypad-s3c64xx.c` implements the S3C64xx GPIO mux path.

### Risks
Rows/columns must match the supplied keymap and the physical GPIO muxing. Board data marked `__initdata` is safe only because the setter copies it.

### Test Signals
Matrix key scanning, wake key behavior, and build coverage with `CONFIG_KEYBOARD_SAMSUNG` validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/keypad.h -->
