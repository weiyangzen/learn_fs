# sources/distributed-fs/ceph-client/drivers/mfd/rsmu_core.c

### Purpose
`rsmu_core.c` is the bus-independent MFD core for Renesas/IDT Synchronization Management Unit devices. It chooses PHC and character-device child names for ClockMatrix, SABRE, and SnowLotus style devices and registers those children once a bus driver has created the appropriate regmap.

### Important APIs, Types, And Functions
Exported functions are `rsmu_core_init()` and `rsmu_core_exit()`. Static cell tables are `rsmu_cm_devs[]` with `8a3400x-phc` and `8a3400x-cdev`, `rsmu_sabre_devs[]` with `82p33x1x-phc` and `82p33x1x-cdev`, and `rsmu_sl_devs[]` with `8v19n85x-phc` and `8v19n85x-cdev`.

### Control Flow
`rsmu_core_init()` switches on `rsmu->type`, selects the matching two-cell table, initializes `rsmu->lock`, and calls `devm_mfd_add_devices()` with two children. Unsupported device types return `-ENODEV`. `rsmu_core_exit()` destroys the mutex on bus-driver remove.

### State, Persistence, And Dependencies
The core initializes the shared `rsmu->lock`, but otherwise stores no private state. Child devices persist for the device-managed lifetime of the parent. Dependencies include MFD core, regmap through the public RSMU data, mutex support, and the bus drivers that populate `rsmu->dev`, `rsmu->type`, and `rsmu->regmap`.

### Integration Points
Both `rsmu_i2c.c` and `rsmu_spi.c` call `rsmu_core_init()` after regmap setup and `rsmu_core_exit()` on remove. The PHC and cdev children consume the parent `struct rsmu_ddata`, regmap, and lock to expose timing/clock synchronization functions.

### Risks
Child names are the binding between this core and downstream PHC/cdev drivers; renaming them breaks autoload/probe. The mutex is destroyed even though MFD children are device-managed, so remove ordering must ensure children are gone or quiesced before `rsmu_core_exit()` returns. Unsupported new RSMU types require adding a cell table here and bus match entries elsewhere.

### Test Signals
Probe tests should validate that each type creates exactly two children with expected names. Error tests should cover unsupported `rsmu->type` and `devm_mfd_add_devices()` failure. Remove/unbind tests should exercise mutex destruction after child teardown on both I2C and SPI parent paths.
