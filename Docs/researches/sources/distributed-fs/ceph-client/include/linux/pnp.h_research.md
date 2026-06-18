# sources/distributed-fs/ceph-client/include/linux/pnp.h

Purpose: defines the Linux Plug and Play bus interface for PNP devices, cards, protocols, resource accessors, driver registration, and protocol-specific ACPI/ISA/BIOS integration.

Important APIs and types: `struct pnp_dev`, `struct pnp_card`, `struct pnp_driver`, `struct pnp_card_driver`, `struct pnp_protocol`, `struct pnp_card_link`, `struct pnp_id`, and `struct pnp_fixup` model devices, multi-function cards, protocol backends, and quirks. Inline helpers expose IO/MEM/IRQ/DMA resource start/end/flags/valid/len, driver data, name and list traversal macros, capability tests, protocol identity checks, and ACPI device extraction. APIs register/unregister drivers and card drivers, attach/detach devices, request/release card devices, auto-configure/start/stop/activate/disable devices, check active/reserved ranges, compare IDs, and identify PNP devices.

Control flow: protocol backends enumerate devices/cards, fill resources/options and IDs, and register with the PNP core. Drivers match against PNP IDs, probe, request resources or card functions, and use activation/configuration helpers unless flags ask not to change resource state. Suspend/resume flows go through driver and protocol callbacks with console-device safeguards.

State and persistence: state is in-memory bus state: global and per-protocol device/card lists, resources/options, active/status/capability flags, card links, proc entries, driver data, and protocol data such as ACPI handles. PNP resources may reflect firmware/hardware configuration but are not persisted by this header.

Dependencies and integration points: integrates with the driver model, `struct resource`, ACPI PNP, ISA PNP, PNPBIOS, console suspend policy, procfs entries, resource reservation, and module driver registration. With `CONFIG_PNP` disabled, registration/configuration helpers return `-ENODEV` or inert defaults, while resource reads return absent values.

Risks and test signals: risks include resource helpers returning sentinel `0` or `-1`, changing resources for console or non-configurable devices, protocol callback NULL checks, card-device lifetime, stale proc entries, and config-disabled callers not handling `-ENODEV`. Test PNPACPI enumeration, resource access for each type, driver probe/remove, card multi-device request/release, suspend/resume with console devices, auto-configuration, and disabled-PNP builds.
