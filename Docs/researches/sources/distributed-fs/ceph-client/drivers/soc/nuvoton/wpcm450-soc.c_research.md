# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/wpcm450-soc.c

## Purpose
Registers Nuvoton WPCM450 SoC identity and revision through the Linux SoC bus.

## Important APIs, Types, And Functions
Key pieces are `struct revision`, `get_revision()`, `wpcm450_soc_init()`, `wpcm450_soc_exit()`, `soc_device_register()`, `soc_device_unregister()`, and `syscon_regmap_lookup_by_compatible()`.

## Control Flow
At module init, the driver exits quietly unless the machine is compatible with `nuvoton,wpcm450`. It looks up the GCR syscon, reads `GCR_PDID`, verifies the chip ID equals `CHIP_WPCM450`, maps the revision byte to a known name, allocates `soc_device_attribute`, and registers the SoC device. Exit unregisters the SoC device and frees the attribute if registration happened.

## State And Persistence
Global pointers `wpcm450_attr` and `wpcm450_soc` hold registered SoC bus state until module exit. Hardware state is read-only from the GCR product ID register.

## Dependencies And Integration Points
Depends on OF machine compatibility, syscon/regmap for `nuvoton,wpcm450-gcr`, and the SoC bus framework. User space can observe the resulting family, SoC ID, and revision through sysfs.

## Risks
Unknown chip or revision returns `-ENODEV` and prevents SoC registration. A missing GCR syscon defers or fails init. The revision table is finite and must be updated for new silicon IDs.

## Test Signals
On WPCM450, `/sys/devices/soc0` should report family `Nuvoton NPCM`, soc_id `WPCM450`, and one of revisions `Z1`, `Z2`, `Z21`, `A1`, `A2`, or `A3`.
