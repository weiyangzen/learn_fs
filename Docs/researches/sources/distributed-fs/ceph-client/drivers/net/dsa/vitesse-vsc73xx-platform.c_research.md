# sources/distributed-fs/ceph-client/drivers/net/dsa/vitesse-vsc73xx-platform.c

Purpose: this file is the platform/MMIO bus frontend for the VSC73xx DSA core. It supports switches attached to a CPU address bus and translates the core's block/subblock/register accesses into big-endian memory-mapped I/O operations.

Important APIs, types, and functions: `struct vsc73xx_platform` stores the platform device, MMIO base, and embedded `struct vsc73xx`. `vsc73xx_make_addr()` encodes block, subblock, and register into the platform address layout. `vsc73xx_platform_read()` and `vsc73xx_platform_write()` implement `struct vsc73xx_ops`. Probe/remove/shutdown bridge the platform driver to `vsc73xx_probe()`, `vsc73xx_remove()`, and `vsc73xx_shutdown()`.

Control flow: probe allocates state with devm, stores drvdata, initializes the embedded core object with device pointer, private pointer, and ops, maps resource 0 with `devm_platform_ioremap_resource()`, and calls the common probe. Remove and shutdown fetch drvdata and delegate to the common core, with shutdown also clearing platform drvdata.

State and persistence: persistent state is only the mapped base address and embedded core state. Register accesses are synchronous and not explicitly locked here; higher layers or the bus ordering provide serialization as needed. Devm owns allocation and mapping lifetimes.

Dependencies and integration points: it depends on platform-driver APIs, OF matching for `vitesse,vsc7385`, `vitesse,vsc7388`, `vitesse,vsc7395`, and `vitesse,vsc7398`, and the shared VSC73xx core ops contract. The hardware is documented as running big-endian by default, so it uses `ioread32be()` and `iowrite32be()`.

Risks: address encoding masks block/subblock fields; invalid block/subblock combinations are rejected by the core helper but invalid register numbers are not separately range-checked. Incorrect endianness or DT resource size will make chip detection fail or corrupt registers. There is no transport-specific locking, so future asynchronous users would need care.

Test signals: platform probe with valid MMIO resource, chip-ID read through big-endian access, common DSA registration, invalid-address rejection, remove/shutdown delegation, and DT compatible coverage for all four switch models.
