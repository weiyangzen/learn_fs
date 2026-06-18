
# sources/distributed-fs/ceph-client/drivers/cxl/acpi.c

Purpose: ACPI platform driver for CXL root discovery. It parses CEDT tables, creates CXL root ports and root decoders, registers host bridge downstream/upstream ports, reflects CXL fixed windows in iomem resources, wires QoS class lookup, and triggers bus rescans.

Important APIs, types, and functions: `cxl_do_xormap_calc()` applies XOR interleave maps and is exported for `cxl_translate`. `cxl_parse_cxims()` parses CXIMS XOR map entries. `cxl_acpi_cfmws_verify()` and `__cxl_parse_cfmws()` validate CFMWS windows and create root decoders. `cxl_acpi_evaluate_qtg_dsm()` / `cxl_acpi_qos_class()` query ACPI QTG IDs. `add_host_bridge_dport()` and `add_host_bridge_uport()` discover ACPI0016 host bridges from CHBS entries. `add_cxl_resources()`, `remove_cxl_resources()`, and `pair_cxl_resource()` manage iomem resource reflection. `cxl_acpi_probe()` orchestrates the full root setup.

Control flow: probe sets a root lock class, allocates a private CXL resource tree, creates a CXL root, installs QoS and optional PRM address-translation ops, scans ACPI host bridges as root dports, registers cleanup for resources, parses all CFMWS windows into root decoders, inserts public CXL iomem resources with overlap trimming, pairs root decoders to public resources, rescans host bridges as upstream CXL ports, optionally creates a root nvdimm bridge for PMEM windows, and calls `cxl_bus_rescan()`. Module init is `subsys_initcall_sync()` so CXL windows are available before consumers such as dax/hmem.

State and persistence: root topology state is devm-managed under the platform device. Root decoders hold HPA ranges, interleave targets, granularity, flags, optional XOR map platform data, cache size, QoS class, and public resource pointer. A private resource tree tracks CXL windows and public resource pairing for cleanup.

Dependencies and integration points: depends on ACPI CEDT/CFMWS/CHBS/CXIMS parsing, ACPI0017 and ACPI0016 device model, PCI root discovery, CXL core port/decoder APIs, HMAT extended cache data, ACPI QTG _DSM, iomem resource APIs, PMEM bridge support, and PRM translation setup from `atl.c`.

Risks and test signals: malformed firmware tables are a central risk; most single-window parse failures are logged but do not fail driver load. XOR interleave requires matching CXIMS or decoder creation fails. Resource expansion/trimming must preserve System RAM conflicts correctly. Mixed CHBS versions disable eRCD support. Test signals include CEDT parsing for modulo and XOR windows, invalid alignment/length, CHBS CXL 1.1 vs 2.0, RCH and VH host bridge paths, QTG _DSM package validation, overlapping CXL/System RAM resources, PMEM bridge creation, and boot ordering with built-in CXL.
