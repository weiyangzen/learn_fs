# Chunk Research: sources/virtualization/nvme-cli/plugins/wdc/wdc-nvme.c lines 1-7532

## Scope

This chunk covers the first half of the Western Digital/SanDisk `nvme-cli` vendor plugin implementation. It defines the device ID matrix, capability bitmask model, WDC/OCP/vendor log page wire formats, UUID constants, helper probes, diagnostic/internal-log dump flows, crash/drive/pfail dump commands, purge commands, C0/C1/C3/C4/C5/CA/D0/firmware-history printers, and the beginning of CA log retrieval. The source tree `sources/virtualization/nvme-cli` is included by `Docs/research_subset_a.md`.

## APIs and Entry Points

- User-visible command handlers in this range include `wdc_cap_diag()`, `wdc_vs_internal_fw_log()`, `wdc_drive_log()`, `wdc_get_crash_dump()`, `wdc_get_pfail_dump()`, `wdc_id_ctrl()`, `wdc_purge()`, and `wdc_purge_monitor()`.
- Device identification and gating helpers are `wdc_get_pci_ids()`, `wdc_get_vendor_id()`, `wdc_check_device()`, `wdc_get_drive_capabilities()`, and `wdc_get_enc_drive_capabilities()`.
- Log support discovery uses NVMe Supported Log Pages first, then WDC C2 device-management entries.
- Dump retrieval primitives use libnvme admin passthrough and standard get-log/telemetry helpers, then write binary output files.

## Core Control Flow

Most command handlers parse CLI options, open an NVMe transport, scan topology, validate WDC/SanDisk vendor support, compute a capability bitmask, and dispatch only if the required capability is present.

Capability detection is a large vendor/device switch. Some devices receive fixed capability masks; others probe log-page support dynamically and use customer firmware ID or C2 marketing-name strings to choose OCP-style features.

Diagnostics can use vendor opcode `0xE6`, DUI opcode `0xFA`, standard NVMe telemetry, or SN730-specific VUC log chunking. Crash and pfail commands fetch a dump length, read the dump, write it, then clear the dump. Purge sends opcode `0xDD`; purge monitor sends opcode `0xDE` and decodes state/progress.

## State and Dependencies

The central state model is the 64-bit `WDC_DRIVE_CAP_*` bitmask. Wire-format structs mirror NVMe/vendor/OCP payloads for C2, E6, DUI variants, SMART/performance logs, OCP C1/C4/C5, firmware activation history, hardware revision, NAND, and PCIe stats.

Dependencies include libnvme transport/identify/get-log/telemetry/admin-passthru APIs, nvme-cli parsing/printing/JSON helpers, WDC utility headers, sysfs PCI ID files, POSIX file APIs, endian conversion helpers, and shell `tar` for archived outputs.

## Risks and Edge Cases

- C2 string parsing copies device-reported lengths into caller buffers without explicit destination-size checks.
- Archive commands pass user-influenced paths to `system()`, making shell quoting/security sensitive.
- Several printers cast byte arrays to integer pointers, which can be alignment-sensitive.
- Capability detection is a hard-coded matrix and can silently miss newer devices/firmware.
- Some JSON printers appear to emit mismatched fields.
- Dump paths allocate based on device-reported sizes.
- V1 DUI section parsing trusts `section_count` without clamping to the fixed array size.

## Cross-Chunk References

- `wdc_get_ca_log_page()` starts here and continues after line 7532.
- Later chunks consume helpers defined here for C1/C3/C4/C5, CA/D0, firmware history, cloud SMART, hardware revision, NAND/PCIe stats, drive status, clear commands, reason ID, drive essentials, resize, enclosure logs, and latency-monitor feature setting.
- Helpers referenced but implemented later include `wdc_get_fw_cust_id()`, drive essentials, resize, drive info, reason ID, enclosure log helpers, and public `run_wdc_*` wrappers.