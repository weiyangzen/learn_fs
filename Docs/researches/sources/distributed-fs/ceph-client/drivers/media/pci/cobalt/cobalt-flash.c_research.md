<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c

Purpose: Exposes the Cobalt board NOR flash as an MTD CFI map through the Cobalt CPU bus window.

Important APIs/functions: `cobalt_flash_probe()` configures a static `map_info`, binds custom read/write/copy callbacks, runs `do_map_probe("cfi_probe")`, sets owner/parent, and registers the MTD device. `cobalt_flash_remove()` unregisters and destroys the MTD map. `flash_read16()`, `flash_write16()`, `flash_copy_from()`, and `flash_copy_to()` translate MTD byte/word accesses to Cobalt bus reads/writes at `COBALT_BUS_FLASH_BASE`.

Control flow: Probe is called after the main Cobalt card is initialized. MTD core subsequently calls map callbacks for reads/writes. Remove tears down only if `cobalt->mtd` exists.

State/persistence: The flash contents are persistent board storage. Driver state is the static `cobalt_flash_map` plus `cobalt->mtd`. `map->virt` is set to BAR1 for each probed card, making the static map unsuitable for multiple cards without serialization/instance separation.

Dependencies/integration: Uses Linux MTD map/CFI APIs and Cobalt bus accessors from `cobalt-driver.h`.

Risks: Static `map_info` is shared across devices, so multiple Cobalt cards could race or overwrite `virt`. `flash_copy_to()` builds 16-bit writes from bytes and logs every copy, which can be noisy. Writes to flash are high risk and depend on correct endian/offset handling.

Test signals: MTD probe success, readback from known flash offsets, erase/write/read cycles on a safe partition, remove cleanup, and multi-card behavior if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.c -->
