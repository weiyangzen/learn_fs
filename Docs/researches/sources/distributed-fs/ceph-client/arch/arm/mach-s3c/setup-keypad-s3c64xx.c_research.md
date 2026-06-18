<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c

### Purpose
Implements S3C64xx keypad GPIO mux configuration.

### Important APIs, Types, And Functions
`samsung_keypad_cfg_gpio(unsigned int rows, unsigned int cols)` configures row and column GPIO ranges for the Samsung keypad controller.

### Control Flow
The keypad platform data/driver calls this architecture hook using the board-provided row and column counts.

### State, Persistence, And Dependencies
State is GPIO alternate-function configuration. Depends on S3C64xx keypad pin layout and Samsung GPIO helpers.

### Integration Points
Used by Cragganmore keypad platform data from `mach-crag6410.c`.

### Risks
Row/column counts outside supported ranges can configure wrong pins. Incorrect muxing causes missing or ghosted keys.

### Test Signals
Matrix key events for every declared key and no ghost events validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-keypad-s3c64xx.c -->
