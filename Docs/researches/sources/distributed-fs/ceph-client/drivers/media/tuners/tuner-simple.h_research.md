# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.h

Purpose: public attach header for the generic simple tuner driver.

APIs/types: declares `simple_tuner_attach(struct dvb_frontend *, struct i2c_adapter *, u8, unsigned int)` when `CONFIG_MEDIA_TUNER_SIMPLE` is reachable. Disabled stub logs and returns `NULL`.

Control flow/state: the `type` argument indexes `tuners[]`; implementation allocates or shares runtime state. Header has no state.

Dependencies/integration: Linux I2C, DVB frontend, and tuner type constants from media headers.

Risks/tests: invalid type IDs fail attach. Build enabled/disabled Kconfig paths and confirm attach installs tuner ops/name for known IDs.
