# sources/distributed-fs/ceph-client/sound/soc/codecs/ntpfw.h

Purpose: declares the shared Neofidelity firmware-loading API used by NTP amplifier codecs.

Important APIs, types, and functions: exposes `int ntpfw_load(struct i2c_client *i2c, const char *name, const u32 magic);`, which loads and validates a firmware image, then writes it to the amplifier over I2C. The header includes Linux I2C and firmware declarations.

Control flow support: callers provide the I2C client, firmware file name, and expected magic. The implementation owns request, parse, transfer, and release operations. The return value is zero on success or a negative errno from firmware loading, validation, allocation-free parsing, or I2C transmission.

State and persistence: no persistent state is declared. Firmware state is transient and owned by `ntpfw.c`; callers must reload after hardware reset when needed.

Dependencies and integration points: included by `ntp8835.c`, `ntp8918.c`, and `ntpfw.c`. The prototype uses `const u32 magic`, while the implementation accepts `u32 magic`; this is ABI-compatible in C but not text-identical.

Risks: the header does not document the binary chunk format beyond "load firmware"; format changes require synchronized implementation and firmware generation. Callers must decide whether `-ENOENT` is fatal.

Test signals: compile users against the declaration, verify exported symbol availability when built as modules, and test callers' error handling for `-ENOENT`, `-EINVAL`, and I2C failures.
