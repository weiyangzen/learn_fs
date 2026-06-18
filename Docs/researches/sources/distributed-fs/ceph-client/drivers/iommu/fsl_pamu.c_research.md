# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu.c

## Purpose

`fsl_pamu.c` is the early platform driver for Freescale/NXP QorIQ PAMU hardware. It allocates and programs the shared primary PAACE table, secondary PAACE table, and operation mapping table, wires access-violation interrupts, disables PAMU bypass in GUTS registers, and enables LIODNs described by device tree so DMA clients can use PAMU identity/window translations.

## Important APIs, Types, and Functions

- `struct pamu_isr_data`: interrupt context with the mapped PAMU register base and PAMU count.
- Global table pointers `ppaact` and `spaact`: software-visible backing storage for hardware PAACE tables.
- `pamu_enable_liodn` / `pamu_disable_liodn`: exported LIODN validity toggles used by the domain layer.
- `pamu_config_ppaace`: programs one primary PAACE window, permissions, stash ID, address translation mode, and optional OMT index.
- `pamu_update_paace_stash`, `get_stash_id`, `get_ome_index`: stash and operation-mapping helpers used by `fsl_pamu_domain.c`.
- `setup_omt`, `setup_liodns`, `setup_one_pamu`: hardware table/register population.
- `pamu_av_isr`: logs access-violation registers, clears violation status, and may disable the offending LIODN.
- `create_csd`: erratum workaround that creates a coherence subdomain with LAW/CSDID programming on listed SoCs.
- `fsl_pamu_probe` and `fsl_pamu_init`: early manual platform-device registration and probe.

## Control Flow

`fsl_pamu_init` runs as an `arch_initcall`, finds the single `fsl,pamu` device-tree node, registers a synthetic platform driver/device, calls `pamu_domain_init`, and then adds the platform device so `fsl_pamu_probe` runs early enough for QMan/BMan users. Probe maps PAMU and GUTS registers, installs the access-violation IRQ, reads capability values, allocates a naturally aligned block for PAACT/SPAACT/OMT, optionally creates a CoreNet coherence subdomain for erratum A-004510, programs every PAMU instance with the table physical ranges, fills the OMT, disables bypass bits, then enables LIODNs from `fsl,liodn` properties.

LIODN setup initializes PAACE entries as primary, coherent, identity/no-translate windows with full permissions, with special QMan/BMan OMT and stash tweaks. Domain-level calls later disable a LIODN, reconfigure the PAACE with window translation and permissions, then re-enable it.

## State and Persistence Behavior

State is in kernel memory and MMIO registers only. `ppaact` persists for the platform lifetime and is shared between all PAMUs. `probed` prevents duplicate probe. PAACE stores are ordered with `mb()` so hardware sees completed descriptor updates before validity changes. There is no remove path; early platform initialization assumes PAMU remains active until reboot.

## Dependencies and Integration Points

The file depends on Open Firmware properties (`fsl,pamu`, `fsl,liodn`, cache nodes, GUTS, LAW, CoreNet CF), PowerPC/QorIQ SPR and CCSR definitions, big-endian MMIO accessors, and the domain APIs declared in `fsl_pamu.h`. It integrates directly with `fsl_pamu_domain.c`, QMan/BMan/CAAM-style LIODN users, and the Linux IRQ subsystem.

## Risks and Edge Cases

- `pamu_get_ppaace` checks `liodn >= PAACE_NUMBER_ENTRIES` but not negative LIODNs.
- Probe allocates one combined table block and has no driver remove path, so failures after table allocation depend on the error path and successful systems intentionally retain mappings.
- `get_stash_id` assumes several device-tree properties exist and traverses cache phandles; malformed CPU/cache nodes can return `~0`.
- `pamu_av_isr` uses `BUG_ON` for unexpected PAACE state or disable failure, turning hardware faults into kernel crashes.
- `setup_one_pamu` ignores its `pamu_reg_size` argument.
- `create_csd` manipulates undocumented CSDID offsets and searches LAW entries with strict assumptions about existing DDR LAW layout.

## Test Signals

Useful coverage includes boot on supported QorIQ device trees, validation of PAACT/SPAACT/OMT physical register programming, LIODN enable/disable and PAACE field checks, QMan/BMan special OMT/stash setup, malformed or missing `fsl,liodn` properties, access-violation IRQ injection, and erratum-path LAW/CSDID programming on matching SVRs.
