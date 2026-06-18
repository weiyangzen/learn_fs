# Group Research: group_1330_nvme_cli_sources_virtualization_nvme_cli_nvme_cmds_h_sources_virtua_695f5e804329

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-cmds.h -->
# File Research: sources/virtualization/nvme-cli/nvme-cmds.h

This header is nvme-cli's convenience command wrapper layer over libnvme passthrough command construction and execution. It is not the main NVMe command implementation; most functions allocate a local `struct libnvme_passthru_cmd`, call a `nvme_init_*()` helper from libnvme, then execute with `libnvme_exec_admin_passthru()`, `libnvme_exec_io_passthru()`, or `libnvme_get_log()`.

Primary command families:
- I/O command wrapper: `nvme_flush()` builds a flush command and executes it through the I/O passthrough path.
- Identify wrappers: generic `nvme_identify()` plus specific controller, active namespace list, namespace, CSI namespace, UUID list, namespace granularity, namespace descriptor list, and ZNS namespace identify helpers.
- Get Log wrappers: covers standard, NVM, ZNS, fabrics/discovery, telemetry, ANA, FDP, endurance, persistent-event, sanitize, SMART, lockdown, reachability, rotational media, power, physical interface, capacity, reservation, and related log pages.
- Feature wrappers: generic and simple `nvme_set_features()` / `nvme_set_features_simple()`, plus generic and simple `nvme_get_features()` / `nvme_get_features_simple()`.
- Namespace attach declarations: `nvme_namespace_attach_ctrls()` and `nvme_namespace_detach_ctrls()` are declared here and implemented in `nvme-cmds.c`.

Important behavior:
- The wrappers centralize common defaults such as `NVME_NSID_ALL`, `NVME_NSID_NONE`, `NVME_CSI_NVM`, fixed structure sizes, default `RAE` handling, and use of `NVME_LOG_PAGE_PDU_SIZE` for selected log pages.
- Result-producing feature commands copy `cmd.result` to the caller-provided `__u64 *result` only after command execution and only when the result pointer is non-null.
- Generic feature commands manually set passthrough fields beyond the initializer defaults, including namespace ID, cdw11-cdw15, data length, user buffer address, and UUID index encoding in cdw14.
- Variable-length log wrappers accept caller-provided lengths and offsets; fixed log wrappers commonly pass `sizeof(*log)`.

Integration role:
- Included by nvme-cli command code and plugins as the stable local shim for common libnvme commands.
- Depends directly on libnvme UAPI types, command enums, structure definitions, field encoding macros, and transport handle APIs.
- Allows plugin code to call concise command helpers such as `nvme_identify_ctrl()`, `nvme_get_log_smart()`, `nvme_get_features()`, and `nvme_set_features()` without hand-building passthrough command structs.

State and ownership:
- No persistent state is stored in this header.
- All command structs are stack-local.
- Caller owns all data buffers passed into identify, log, and feature commands.

Risk notes:
- This is a broad API surface; small changes can affect core nvme-cli commands and many vendor plugins.
- Wrapper correctness depends on exact NVMe command dword, namespace, log identifier, RAE, LSP, LSI, offset, length, and UUID-index semantics.
- Some parameters are only meaningful if forwarded correctly through either the local wrapper or the libnvme initializer. Audit carefully before edits, especially wrappers with `rae`, `nsid`, `len`, and offset parameters.
- The header exposes many `static inline` functions, so behavior changes compile into every caller rather than a single object file.
- Good tests should include representative identify, log, feature, namespace attach/detach, and plugin call paths, preferably with mocked passthrough command inspection where hardware is unavailable.

<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-cmds.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-dummy.c -->
# File Research: sources/virtualization/nvme-cli/nvme-dummy.c

This is a minimal dummy executable used for Windows port bring-up.

Behavior:
- Includes `<stdio.h>`.
- Defines `main()`.
- Prints `This is a dummy executable for windows port bring up.`.
- Returns success.

Integration role:
- Provides a placeholder binary target where the real nvme-cli executable is not yet available or not suitable during Windows build scaffolding.

Risk notes:
- No command-line arguments are used.
- No NVMe or filesystem behavior exists here.
- Any change should preserve its role as a trivial build/portability placeholder unless the Windows port strategy changes.

<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-models.c -->
# File Research: sources/virtualization/nvme-cli/nvme-models.c

This file resolves a Linux NVMe controller device name such as `nvme0` into a human-readable PCI product/model description. It reads controller identity values from sysfs, parses a `pci.ids` database, and formats the best available vendor/device/class description.

Public API:
- `nvme_product_name(const char *devname)`: accepts either a bare device name or a path with a final `nvme%d` component, extracts the controller index, and returns a newly allocated product string or `NULL`.

Main flow:
- `nvme_product_name()` strips any leading path with `strrchr()`, validates the final component with `sscanf("nvme%d")`, then delegates to `__nvme_product_name()`.
- `__nvme_product_name()` opens `pci.ids`, builds sysfs paths for `/sys/class/nvme/nvme%d/device/{subsystem_vendor,subsystem_device,vendor,device,class}`, reads those values, scans `pci.ids`, and formats a result string.
- `open_pci_ids()` prefers `PCI_IDS_PATH` when set, otherwise searches common distro locations: `/usr/share/hwdata/pci.ids`, `/usr/share/pci.ids`, and `/usr/share/misc/pci.ids`.
- `parse_vendor_device()` walks indented `pci.ids` device and subsystem-device entries after a vendor match.
- `pull_class_info()` finds class, subclass, and programming-interface descriptions.
- `format_all()` and `format_and_print()` combine class, vendor, device, and subsystem matches into a single display string, falling back to `"Unknown device"`.

Important helpers:
- `read_sys_node()` opens and reads one sysfs attribute, strips a trailing newline, and reports non-ENOENT open errors.
- `is_top_level_match()`, `is_mid_level_match()`, `is_inner_sub_vendev()`, and `is_final_match()` encode the expected indentation and field layout of `pci.ids`.
- `locate_info()` skips numeric fields in matched `pci.ids` lines to return the human-readable text.
- `free_all()` releases static parse-result strings after each lookup.

State and ownership:
- Uses static path buffers and static parse-result pointers for intermediate state.
- The returned product string is heap allocated; callers must free it.
- The implementation is not thread-safe because intermediate parse state is global.

Risk notes:
- Parsing is tightly coupled to `pci.ids` indentation and field widths.
- Several match helpers use fixed-offset `memcmp()` calls, so malformed or unexpectedly short lines could be risky.
- `read_sys_node()` does not explicitly handle `read()` returning `-1` before indexing the buffer, which is a robustness hazard.
- Missing sysfs data, missing `pci.ids`, or an invalid `PCI_IDS_PATH` returns `NULL` or a fallback display string depending on where lookup fails.
- This file is Linux/sysfs-specific and should not be treated as portable device-model discovery code.

<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-models.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-models.h -->
# File Research: sources/virtualization/nvme-cli/nvme-models.h

This header declares the product-name lookup API implemented by `nvme-models.c`.

Public API:
- `char *nvme_product_name(const char *devname);`

Integration role:
- Used by nvme-cli printing code to enrich controller output with a PCI-derived product/model name.
- The returned pointer is owned by the caller and should be freed.

Risk notes:
- The header does not document ownership, but the implementation returns allocated memory.
- Any signature change affects output paths that call `nvme_product_name()` while rendering controller information.

<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-models.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-binary.c -->
# File Research: sources/virtualization/nvme-cli/nvme-print-binary.c

This file implements the binary output backend for nvme-cli's print abstraction. Instead of formatting NVMe structures as text or JSON, its callbacks dump the raw bytes with `d_raw()`.

Public API:
- `struct print_ops *nvme_get_binary_print_ops(nvme_print_flags_t flags)`: sets `binary_print_ops.flags` and returns the singleton binary print operation table.

Main behavior:
- Most callbacks are small adapters that cast a typed NVMe structure to `unsigned char *` and pass a byte length to `d_raw()`.
- Fixed-size structures use `sizeof(*ptr)`.
- Variable-size logs use caller-supplied lengths or lengths derived from little-endian fields inside the returned NVMe structure.
- Unsupported or non-binary-relevant print operations are intentionally set to `NULL` in the `print_ops` table.

Covered output families:
- Identify data: controller, namespace, command-set independent namespace, NVM namespace, ZNS controller/namespace, UUID list, NVM set list, domain list, namespace granularity, namespace descriptors.
- Logs: error, firmware slot, SMART, supported logs, endurance, ANA, self-test, sanitize, LBA status, persistent event, reservation notification, telemetry-related aggregate/event logs, FDP logs, media unit, capacity, management address, rotational media, reachability, discovery, host discovery, AVE discovery, pull-model DDC request, power measurement, and ZNS changed zones.
- Other binary outputs: controller registers, reservation report, directive buffers, feature data buffers, discovery log records, and effects-log list entries.

Notable length handling:
- `binary_phy_rx_eom_log()` computes output length from `hsize`, and when measurement is complete includes `dsize * nd`.
- `binary_discovery_log()` dumps the discovery log header plus `numrec` discovery entries.
- `binary_dispersed_ns_psub_log()` includes `numpsub * NVME_NQN_LENGTH`.
- Host/AVE/pull-model discovery logs use total-length fields from the structure.
- Zone reports, ANA logs, boot partition logs, LBA status, FDP config/usage/status, and several aggregate logs rely on a size passed by the caller.

Integration role:
- Selected by `nvme-print.c` when binary output is requested.
- Shares the same `struct print_ops` interface as stdout and JSON printers, allowing command code to remain mostly output-format agnostic.
- Depends on `nvme-print.h`, `logging.h`, and `common.h`, including `d_raw()`, endian helpers, NVMe structure definitions, and `list_head` iteration.

State and ownership:
- Uses one static `binary_print_ops` table.
- `nvme_get_binary_print_ops()` mutates only the table's `flags` field before returning it.
- The backend does not allocate, transform, or retain command data.

Risk notes:
- Binary output correctness depends almost entirely on exact length selection. A too-small length truncates data; a too-large length can expose uninitialized or unrelated memory.
- Several lengths are derived from device-provided little-endian fields, so callers must ensure buffers are at least that large before invoking the print callback.
- Because many `print_ops` entries are `NULL`, new command output paths must either tolerate absent binary callbacks or add matching binary handlers.
- The singleton operation table is simple but not isolated per caller; concurrent use with different flags would share mutable state.

<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/nvme-print-binary.c -->