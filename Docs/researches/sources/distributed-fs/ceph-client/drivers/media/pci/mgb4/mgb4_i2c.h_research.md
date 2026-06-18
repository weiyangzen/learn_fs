# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_i2c.h

- Purpose: Defines MGB4 I2C client wrapper and register-value configuration API.
- Important APIs/types/functions: `struct mgb4_i2c_client`, `struct mgb4_i2c_kv`, and helper prototypes.
- Control flow: Vin/vout/core create wrappers for extender, deserializer, and serializer chips and use keyed register arrays for setup.
- State and persistence: State is limited to the Linux I2C client pointer and address-size selector.
- Dependencies and integration points: Integrated with Linux I2C core and MGB4 sysfs/configuration modules.
- Risks: Address size is an int convention, not an enum; invalid values fall into 16-bit path.
- Test signals: Compile and serializer/deserializer register tests.
