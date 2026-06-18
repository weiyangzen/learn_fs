<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c

### Purpose
Configures S3C64xx GPIO pins for I2C bus 0.

### Important APIs, Types, And Functions
`s3c_i2c0_cfg_gpio(struct platform_device *dev)` sets the bus-0 SDA/SCL pins to the proper alternate function and pull state.

### Control Flow
I2C platform data names this callback and the I2C controller setup calls it before bus operation.

### State, Persistence, And Dependencies
State is GPIO mux/pull hardware configuration. Depends on S3C64xx GPIO helpers.

### Integration Points
Cragganmore registers PMIC and RTC devices on bus 0.

### Risks
Wrong pinmux or pull configuration prevents all bus-0 I2C devices from probing.

### Test Signals
I2C bus scan/probe for WM831x/RTC devices validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c -->
