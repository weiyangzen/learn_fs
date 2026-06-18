## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/base.c

### Purpose
`base.c` is the central NVKM device core. It keeps the global device registry, maps BAR0 PRI MMIO, identifies chipsets, selects the per-chip subdevice/engine constructor table, constructs all subdevices from `core/layout.h`, and drives device preinit/init/fini/delete lifecycle.

### Important APIs, types, and functions
Public functions include `nvkm_device_find()`, `nvkm_device_subdev()`, `nvkm_device_engine()`, `nvkm_device_fini()`, `nvkm_device_init()`, `nvkm_device_del()`, and `nvkm_device_ctor()`. Internal helpers include `nvkm_device_find_locked()`, `nvkm_device_preinit()`, and `nvkm_device_endianness()`. The bulk of the file is `static const struct nvkm_device_chip` tables for NV04 through GB20x families, mapping subdevice/engine instance masks to constructor functions.

### Control flow
Construction is serialized by `nv_devices_mutex`, rejects duplicate handles, maps PRI MMIO, switches GPU endianness if needed, reads boot registers, applies optional `NvChipset` override, derives chipset/card type, selects the matching chipset table, rejects unsupported vGPU modes on TU100+, reads strap bits to set crystal frequency, initializes interrupts, then expands `core/layout.h` macros to construct each singleton or instanced subdevice indicated by the selected table. `-ENODEV` constructors are treated as absent optional components; other errors abort construction.

Preinit unarms interrupts, calls device preinit, preinits subdevices in list order, runs devinit post, parses top topology, and unlocks framebuffer memory. Full init calls preinit, powers off existing state, rearms interrupts, runs device init, initializes subdevices in list order, registers ACPI notification, and enables thermal clock gating. Fini unregisters ACPI, finishes subdevices in reverse order, disables thermal clock gating, calls device fini, and unarms interrupts. Suspend failures trigger restart of already-finished subdevices. Delete destroys interrupt infrastructure, deletes subdevices in reverse order, unmaps PRI, removes the device from the registry, calls backend destructor, and frees memory.

### State and persistence behavior
Global state is `nv_devices`, protected by `nv_devices_mutex`. Per-device persistent state includes backend function table, quirk pointer, Linux device pointer, type, handle, config/debug option strings, name, debug level, MMIO mapping, chipset metadata, crystal frequency, interrupt state, subdevice list, and direct pointers to constructed subdevices/engine arrays. The chipset tables are static read-only hardware support data.

### Dependencies
It depends on `priv.h`, `acpi.h`, option parsing, BIOS and thermal helpers, interrupt helpers, devinit/top/fb helpers, all subdevice and engine constructor declarations, Linux `ioremap()`/`iounmap()`, MMIO helpers, list/mutex primitives, and `core/layout.h`.

### Integration points
PCI, Tegra, and user-facing device layers call `nvkm_device_ctor()` with platform-specific resource functions. Every subdevice/engine constructor referenced in the chipset tables is integrated through this file. The control object, FIFO, display, GR, memory, firmware/GSP, and CE engines are all selected from these tables based on chipset.

### Risks
This file has very high blast radius. A wrong chipset table entry can instantiate incompatible hardware blocks, omit required firmware managers, expose invalid engine counts, or break probe for a whole GPU family. The `NvChipset` and unsupported-chipset options are development paths that can force mismatched tables. Endianness switching and BAR mapping failures occur early and must clean up correctly. Treating `-ENODEV` as optional is necessary for GSP-owned components but can hide unexpected missing hardware if constructors overuse it.

### Test signals
Essential signals include build/link coverage for all constructor symbols, probe tests across representative NV04/NV50/Fermi/Kepler/Maxwell/Pascal/Volta/Turing/Ampere/Ada/Blackwell devices, duplicate handle rejection, vGPU rejection on TU100+, suspend/resume and runtime suspend rollback, GSP-RM device modes, optional constructor `-ENODEV` handling, ACPI notifier registration, and teardown leak/error checks.
