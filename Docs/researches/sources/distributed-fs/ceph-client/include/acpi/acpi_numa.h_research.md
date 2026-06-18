<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h

## Purpose
`acpi_numa.h` declares Linux ACPI NUMA mapping helpers for translating ACPI proximity domains (PXMs) from SRAT/HMAT data into kernel NUMA node IDs. It also exposes control hooks for disabling SRAT and HMAT handling after invalid firmware data.

## Important APIs, types, and functions
When `CONFIG_ACPI_NUMA` is enabled, the header defines `MAX_PXM_DOMAINS`, declares `pxm_to_node()`, `node_to_pxm()`, `acpi_map_pxm_to_node()`, `acpi_srat_revision`, `disable_srat()`, `fix_pxm_node_maps()`, `bad_srat()`, and `srat_disabled()`. When disabled, `fix_pxm_node_maps()`, `disable_srat()`, `pxm_to_node()`, and `node_to_pxm()` become harmless stubs. `disable_hmat()` is separately gated by `CONFIG_ACPI_HMAT`.

## Control flow
SRAT parsing maps firmware proximity domains to kernel node IDs through `acpi_map_pxm_to_node()` and later resolves in both directions through `pxm_to_node()` and `node_to_pxm()`. If SRAT validation fails, callers invoke `bad_srat()` or `disable_srat()`; HMAT parsing can be disabled independently.

## State and persistence behavior
The mapping state lives in NUMA implementation files and is derived at boot from ACPI SRAT/HMAT tables. Firmware tables are persistent boot inputs; kernel maps are runtime-only and may be invalidated if table checks fail.

## Dependencies and integration points
It depends on Linux NUMA definitions when enabled and integrates ACPI SRAT/HMAT parsing with memory topology, CPU/node affinity, device locality, and heterogeneous memory attributes. It is used by architecture-specific ACPI boot paths and memory-management code.

## Risks and test signals
Risks include exceeding PXM domain limits, firmware SRAT revisions changing semantics, stale node/PXM maps after validation failure, disabled stubs silently collapsing all PXMs to node 0, and HMAT remaining enabled after SRAT rejection. Test signals include SRAT systems with PXM values above 255, invalid SRAT fallback, node-to-PXM round trips, `fix_pxm_node_maps()` after sparse node assignment, HMAT disable behavior, and `CONFIG_ACPI_NUMA=n` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_numa.h -->
