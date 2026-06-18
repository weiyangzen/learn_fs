<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for I2C bus 1.

### Important APIs, Types, And Functions
`s3c_i2c1_cfg_gpio(struct platform_device *dev)` applies the bus-1 SDA/SCL alternate function and pull configuration.

### Control Flow
The I2C controller platform setup invokes this callback before registering or using bus 1.

### State, Persistence, And Dependencies
State is hardware pinmux. Depends on S3C64xx GPIO helpers and platform I2C data.

### Integration Points
Cragganmore uses bus 1 for module ID devices and audio codecs.

### Risks
Any misconfiguration blocks module probing and codec registration.

### Test Signals
Successful bus-1 device probing, especially `"wlf-gf-module"` and WM8311, validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c -->
