# sources/distributed-fs/ceph-client/drivers/hwmon/occ/p8_i2c.c

Purpose: POWER8 OCC transport frontend using a BMC I2C connection to access on-chip control bridge SCOM registers and exchange OCC commands through SRAM windows.

Important APIs/types/functions: `struct p8_i2c_occ` embeds `struct occ` with an I2C client. Low-level helpers are `p8_i2c_occ_getscom()`, `p8_i2c_occ_putscom()`, `p8_i2c_occ_putscom_u32()`, `p8_i2c_occ_putscom_be()`, and transport callback `p8_i2c_occ_send_cmd()`. Probe/remove bind this transport to common OCC setup/shutdown.

Control flow: `send_cmd` writes the OCC command SRAM address to OCB, writes the big-endian command through `OCB_DATA3`, triggers data attention through `OCB_DATA1`, then repeatedly reads the response SRAM header until return status is no longer command-in-progress or a one-second timeout expires. It maps OCC response status to Linux errors, validates response length, and fetches remaining 8-byte chunks.

State and persistence: persistent state is the embedded OCC object and I2C client. Common code stores the response and active/error state. Hardware state includes selected OCB address and OCC command processing.

Dependencies and integration: depends on I2C transfers, FSI OCC response status constants, scheduler timeout, unaligned big-endian access, and OF compatible `ibm,p8-occ-hwmon`. Probe sets 250 us power sample time and poll command data `0x10`.

Risks: SCOM address shifting and endian conversions are subtle. The polling loop uses interruptible sleep without checking pending signals. It assumes response chunks can be fetched sequentially by repeated reads. Partial I2C sends are treated as `-EIO`.

Test signals: P8 BMC I2C communication, command-in-progress timeout, all OCC response status mappings, response length bounds, multi-chunk response reads, OF match probe, and clean common shutdown on remove.
