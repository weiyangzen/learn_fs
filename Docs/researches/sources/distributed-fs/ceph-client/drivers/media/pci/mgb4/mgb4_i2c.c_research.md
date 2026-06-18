# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.c

- Purpose: Helper layer for serializer/deserializer I2C access with either 8-bit SMBus registers or 16-bit register-address transfers.
- Important APIs/types/functions: `mgb4_i2c_init/free`, `mgb4_i2c_read_byte`, `mgb4_i2c_write_byte`, `mgb4_i2c_mask_byte`, `mgb4_i2c_configure`, and internal `read_r16/write_r16`.
- Control flow: Init creates an I2C client for a board-info address and stores address width. Read/write dispatch to SMBus byte ops for 8-bit devices or custom two-byte register prefix messages for 16-bit devices. Mask helper read-modify-writes unless mask is full; configure applies register-value arrays.
- State and persistence: State is an `i2c_client` pointer and address width in endpoint structs; serializer/deserializer registers are persistent only until chip reset.
- Dependencies and integration points: Used by core module detection, vin deserializer init/sysfs, and vout serializer init/sysfs. Protected by `mgbdev->i2c_lock` at call sites that need bus serialization.
- Risks: 16-bit write buffer supports only two payload bytes beyond address; current byte writes fit. Callers must hold locks consistently. `mgb4_i2c_free` assumes a valid client.
- Test signals: Test 8-bit FPDL/GMSL1 and 16-bit GMSL3 devices, NACK handling, masked writes, and configuration arrays.
