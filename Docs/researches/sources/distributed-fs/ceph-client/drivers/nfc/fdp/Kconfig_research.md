# sources/distributed-fs/ceph-client/drivers/nfc/fdp/Kconfig

Purpose: Defines build-time options for the Intel Fields Peak NFC controller core and its I2C transport.

Important APIs, types, and functions: `NFC_FDP` is the core NCI driver and depends on `NFC_NCI`, selecting `CRC_CCITT`. `NFC_FDP_I2C` depends on `NFC_FDP && I2C` and builds the I2C physical layer module.

Control flow: Build-time only. Selecting the I2C transport also requires the core driver, and the help text documents module names `fdp` and `fdp_i2c`.

State and persistence behavior: Configuration state persists in `.config`; no runtime state exists here.

Dependencies and integration points: Connects the FDP core in `fdp.c` and I2C transport in `i2c.c` to the NFC NCI subsystem and Kbuild.

Risks: If transport dependencies drift from source includes, builds can fail. `CRC_CCITT` is selected although the visible FDP I2C LRC path does not directly use it, so this dependency should be checked against core firmware/protocol needs before changes.

Test signals: Build `CONFIG_NFC_FDP=m`, `CONFIG_NFC_FDP_I2C=m`, built-in variants, and dependency-disabled configs without `I2C` or `NFC_NCI`.
