# sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001_priv.h

Purpose: private definitions for TUA9001 implementation state and register tables.

APIs/types: `struct tua9001_reg_val` stores 8-bit register/16-bit value pairs. `struct tua9001_dev` stores the frontend, I2C client, and regmap.

Control flow/state: allocated in probe, assigned to `fe->tuner_priv`, used by init/tune/sleep/remove, and freed on remove. Regmap is devm-managed.

Dependencies/integration: includes `tua9001.h`, `linux/math64.h`, and `linux/regmap.h`.

Risks/tests: lifetime must remain valid for both I2C client data and frontend private data. Test probe failure unwinding, remove, and regmap error handling.
