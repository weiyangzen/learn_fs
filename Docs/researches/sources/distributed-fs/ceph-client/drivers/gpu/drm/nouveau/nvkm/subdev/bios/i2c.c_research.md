<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c

### Purpose

Parser for DCB I2C bus tables. It maps logical I2C indices used by DCB outputs and init scripts to bus type, drive/sense pins, and AUX/I2C metadata.

### Important APIs, types, and functions

`dcb_i2c_table()`, entry accessors, parse and match helpers decode `struct dcb_i2c_entry` values from versioned DCB I2C tables.

### Control flow

The parser locates the I2C table from DCB metadata, validates version/header/count/length, indexes entries, and decodes bus type and pin assignments according to table version.

### State and persistence behavior

No runtime state is kept here. The I2C subdevice owns bus objects created from decoded records.

### Dependencies and integration points

Depends on DCB and BIOS access helpers. Display output probing, connector detection, AUX routing, and BIOS init I2C opcodes depend on these records.

### Risks

Wrong I2C table parsing can probe EDID or external devices on the wrong bus. Legacy table handling is compatibility-sensitive.

### Test signals

Source read size: 164 lines, 4773 bytes. EDID read tests across DCB outputs, AUX/I2C bus enumeration, init-script I2C opcode tests, and VBIOS dump comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/i2c.c -->
