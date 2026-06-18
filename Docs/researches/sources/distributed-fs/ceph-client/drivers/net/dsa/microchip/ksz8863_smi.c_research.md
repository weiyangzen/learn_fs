# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8863_smi.c

Purpose: SMI-over-MDIO transport for Microchip KSZ8863 and KSZ8873 switches, exposing 8/16/32-bit regmaps to the common KSZ switch framework.

Important APIs/types/functions: `ksz8863_mdio_read()`/`write()` implement custom regmap bus access using raw mdiobus operations under nested lock. `regmap_smi[]` supplies buses for three value widths. `ksz8863_regmap_config[]` defines register format, no cache, common regmap locking, and `U8_MAX` range. Probe allocates `ksz_device`, initializes regmaps with chip access tables, and calls `ksz_switch_register()`.

Control flow: MDIO probe retrieves match chip data, creates regmaps, copies optional platform data, registers the switch, and stores drvdata. Remove calls `ksz_switch_remove()`. Shutdown calls `dsa_switch_shutdown()` and clears drvdata.

State and persistence: `ksz_device` stores transport state, with `dev->priv` as the MDIO device. Regmaps are uncached; hardware is the source of truth. Access is serialized by nested `mdio_lock`.

Dependencies and integration: MDIO, regmap custom buses, KSZ common framework, `ksz_switch_chips[KSZ88X3]`, and OF compatibles `"microchip,ksz8863"`/`"microchip,ksz8873"`.

Risks and test signals: SMI address encoding, write-buffer pointer arithmetic, 16/32-bit endianness, lock nesting, and deferred registration. Test regmap reads/writes, common chip detection, no lockdep warnings, cleanup, and KSZ8 callbacks over SMI.
