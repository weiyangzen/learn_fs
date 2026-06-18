# sources/distributed-fs/ceph-client/drivers/acpi/mipi-disco-img.c

Purpose: `mipi-disco-img.c` implements ACPI MIPI DisCo for Imaging support. It parses ACPI 6.5 `_CRS` CSI-2 serial-bus descriptors and MIPI imaging `_DSD` properties, then constructs Linux software-node graph endpoints compatible with the generic fwnode graph model used by V4L2.

Important APIs, types, and functions: exported internal ACPI helpers are `acpi_mipi_check_crs_csi2()`, `acpi_mipi_scan_crs_csi2()`, `acpi_mipi_init_crs_csi2_swnodes()`, `acpi_mipi_crs_csi2_cleanup()`, and x86-only `acpi_graph_ignore_port()`. Key structures are `struct crs_csi2_connection`, `struct crs_csi2`, and `struct csi2_resources_walk_data`. Core helpers parse resources, allocate software-node storage, connect local/remote endpoints, copy MIPI properties, and register node groups.

Control flow: during ACPI scan, `acpi_mipi_check_crs_csi2()` walks each device `_CRS`, collects CSI-2 descriptors, resolves remote handles, and attaches per-handle data. `acpi_mipi_scan_crs_csi2()` counts local and remote port needs, creates placeholder entries for remote endpoints lacking descriptors, allocates software-node arrays for every participant, then wires endpoint `remote-endpoint`, `bus-type`, and `reg` properties. After ACPI devices exist, `acpi_mipi_init_crs_csi2_swnodes()` fetches each `struct acpi_device`, derives device properties such as rotation, clock frequency, LED/flash limits, reads per-port MIPI lane properties from `_DSD`, registers software nodes, and attaches them as secondary fwnodes. Cleanup releases temporary entries and unattached software-node memory.

State and persistence: temporary scan state is kept in the global `acpi_mipi_crs_csi2_list` and per-handle attached data. Successfully registered software nodes are transferred to `adev->swnodes` and the ACPI fwnode secondary pointer; temporary ownership is cleared to avoid premature freeing.

Dependencies and integration: depends on ACPI resource parsing, ACPI per-handle data attachment, Linux software nodes, generic property/fwnode APIs, V4L2 fwnode bus type constants, ACPI scan locking, and x86 DMI/CPU matching for Dell broken graph quirks.

Risks: this is allocation- and firmware-data-heavy. Overflow checks protect software-node allocation, but malformed remote references, unsupported PHY types, missing port data nodes, and too many lane/frequency entries can silently omit graph details. The lifecycle is split across early scan, device enumeration, and cleanup, so ownership transfer bugs can leak or double-free. The Dell x86 quirk intentionally ignores some firmware graph nodes based on DMI and CPU generation.

Test signals: validate two-endpoint CSI-2 graph creation, remote placeholder devices, C-PHY and D-PHY bus types, lane and polarity property translation, link-frequency limits, `_PLD` rotation fallback, software-node registration failure, cleanup before and after ownership transfer, and Dell IPU/LNK port-ignore matching.
