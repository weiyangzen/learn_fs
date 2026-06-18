<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c

### Purpose

ACPI `_ROM` shadow backends for reading VBIOS from platform firmware. It provides fast and spec-compliant slow variants.

### Important APIs, types, and functions

`nvbios_acpi_fast` and `nvbios_acpi_slow` are `nvbios_source` instances. Helpers evaluate ACPI ROM with offset/length arguments and read chunks into `bios->data`.

### Control flow

The fast reader rounds requests to 4 KiB boundaries and fetches larger blocks for speed; the slow reader follows smaller access expectations. Init locates the ACPI ROM handle, read calls evaluate it, and fini has no complex state.

### State and persistence behavior

Backend state is the ACPI handle. The selected image is later owned by `bios->data` if this source wins.

### Dependencies and integration points

Depends on ACPI and x86 config, Linux ACPI object evaluation, and the shadow-source interface. It is one of the fallback sources used by `shadow.c`.

### Risks

ACPI firmware can reject large reads or return short buffers; fast mode deliberately bends the spec and may fail where slow mode works. Non-ACPI builds return errors.

### Test signals

Source read size: 140 lines, 4001 bytes. Laptop boot tests, fast-vs-slow fallback timing, ACPI failure injection, and validation on systems where PCI ROM is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowacpi.c -->
