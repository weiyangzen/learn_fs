<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h

Purpose: Declares Cobalt NOR flash lifecycle helpers.

Important APIs/types: `cobalt_flash_probe(struct cobalt *cobalt)` registers the flash MTD map. `cobalt_flash_remove(struct cobalt *cobalt)` unregisters and destroys it.

Control flow: Called from Cobalt PCI probe/remove after the device and BARs are live.

State/persistence: No header state; functions operate on persistent NOR flash and `cobalt->mtd`.

Dependencies/integration: Includes `cobalt-driver.h` for the card state and bus accessors used by the implementation.

Risks: The simple lifecycle API does not expose detailed MTD probe errors to the main probe path, which currently ignores flash probe failure.

Test signals: Compile/link checks and MTD device appearance/removal after Cobalt probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-flash.h -->
