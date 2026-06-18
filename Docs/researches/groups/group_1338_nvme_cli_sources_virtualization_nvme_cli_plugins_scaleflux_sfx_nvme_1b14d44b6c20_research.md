# Group Research: group_1338_nvme_cli_sources_virtualization_nvme_cli_plugins_scaleflux_sfx_nvme_1b14d44b6c20

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nvme-cli`. Every requested source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.c

ScaleFlux nvme-cli plugin implementation. It provides vendor-specific ScaleFlux commands for SMART extension logs, latency logs, bad-block data, dynamic capacity management, internal feature get/set, persistent event log dumping/parsing, namespace expansion, and a combined device status view.

Key command handlers:
- `get_additional_smart_log`: retrieves vendor log page `0xca` with `nvme_get_nsid_log`, printing normal, JSON, or raw binary output.
- `get_lat_stats_log`: retrieves read/write latency stats from log IDs `0xc1`/`0xc3`, detects Vanda version `0.0` or Myrtle `4.1`, and prints bucket histograms.
- `sfx_get_bad_block`: retrieves bad block table from `SFX_LOG_BBT`/`0xc7`, expecting exactly `256 * 4096` bytes, then prints counts and remap tables.
- `query_cap_info`: calls `nvme_query_cap`, using ioctl `SFX_GET_FREESPACE` first and falling back to admin opcode `0xd3`.
- `change_cap`: converts GB or byte capacity to 4 KiB units, sanity-checks against provisioned capacity and free RAM, prompts for shrink unless `--force`, sends admin opcode `0xd4`, and rereads partitions with `BLKRRPART`.
- `sfx_set_feature` / `sfx_get_feature`: use vendor admin opcodes `0xd5`/`0xd6`; feature IDs include atomic writes, update provision capacity, and clean card.
- `sfx_dump_evtlog`: dumps NVMe persistent event log, optionally parses ScaleFlux-specific event records into a text file.
- `sfx_expand_cap`: expands the last namespace with `nvme_admin_ns_mgmt` cdw10 `0x0e` and a packed ScaleFlux payload.
- `sfx_status`: aggregates sysfs PCIe data, identify controller, SMART, ScaleFlux extended health, additional SMART, capacity/freespace, and atomic feature state into human or JSON output.

Important internal flows:
- `nvme_query_cap` uses a Linux ioctl path when available, otherwise uses vendor passthrough. This makes behavior dependent on both kernel driver support and controller firmware support.
- Capacity conversion uses IDEMA formulas and assumes sector/LBA relationships in `IDEMA_CAP`, `IDEMA_CAP2GB`, and `IDEMA_CAP2GB_LDS`.
- `change_sanity_check` enforces target capacity between 1x and 4x provisioned capacity and estimates memory needed for capacity expansion.
- `sfx_clean_card` validates the handle is a character controller device before issuing `NVME_IOCTL_CLR_CARD`.

Notable edge cases:
- `sfx_dump_evtlog` returns `0` from the CLI handler even after assigning `err`, so caller-visible failure propagation is incomplete.
- Event parsing indexes `sfx_evtlog_warning[code_type]` and `sfx_evtlog_error[code_type]` without explicit bounds checks after decoding firmware event codes.
- `sfx_status` depends heavily on Linux sysfs paths under `/sys/class/nvme/<ctrl>/device/*`; missing AER/link files cause hard failure.
- Namespace derivation in `sfx_expand_cap` falls back to the last character of the device name for namespace ID when invoked on a namespace handle, which is fragile for multi-digit namespace IDs.

External dependencies:
- libnvme admin passthrough/get-log helpers.
- nvme-cli shared parsing/output helpers.
- Linux ioctls `BLKRRPART`, `SFX_GET_FREESPACE`, and `NVME_IOCTL_CLR_CARD`.
- sysfs PCIe/NVMe attributes for `sfx_status`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.h

ScaleFlux plugin command registration header. It defines `CMD_INC_FILE` as `plugins/scaleflux/sfx-nvme`, includes `cmd.h`, and registers the `sfx` plugin with description `ScaleFlux vendor specific extensions`.

Registered commands:
- `smart-log-add` -> `get_additional_smart_log`
- `lat-stats` -> `get_lat_stats_log`
- `get-bad-block` -> `sfx_get_bad_block`
- `query-cap` -> `query_cap_info`
- `change-cap` -> `change_cap`
- `set-feature` -> `sfx_set_feature`
- `get-feature` -> `sfx_get_feature`
- `dump-evtlog` -> `sfx_dump_evtlog`
- `expand-cap` -> `sfx_expand_cap`
- `status` -> `sfx_status`

This header is consumed by nvme-cli’s command-generation mechanism via `CREATE_CMD` in the `.c` file and final `define_cmd.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-types.h -->
# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-types.h

ScaleFlux vendor type and constant definitions used by `sfx-nvme.c`.

Key constants:
- Vendor log IDs: latency read/write `0xc1`/`0xc3`, extended health `0xc2`, BBT `0xc7`, identify `0xcc`, alternate extended health `0xd2`.
- Feature IDs: atomic `0x01`, update provision capacity `0xac`, clean card `0xdc`.
- Vendor admin opcodes: query capacity `0xd3`, change capacity `0xd4`, set feature `0xd5`, get feature `0xd6`.
- Critical warning bits: power-fail data loss, over capacity, read/write lock.

Key structs:
- `sfx_freespace_ctx`: capacity/freespace fields in sector or 4 KiB units, map unit, max user space, and friendly capacity support.
- `nvme_additional_smart_log_item`: packed 12-byte-ish SMART item with normalized value and 6-byte raw payload, including union views for wear leveling and thermal throttling.
- `nvme_additional_smart_log`: ordered list of ScaleFlux additional SMART counters.
- `sfx_lat_stats_vanda` and `sfx_lat_stats_myrtle`: two firmware-generation-specific latency histogram layouts.
- `sfx_lat_stats`: union overlay allowing major/minor version probing before selecting the concrete layout.
- `extended_health_info_myrtle`: ScaleFlux extended health page fields used by status output, including OPN, physical capacity, compression ratio, power, IO speed, formatted capacity, and critical warning bits.

The file is pure shared layout. It must remain ABI-compatible with ScaleFlux firmware log/admin payloads.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-diag.h -->
# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-diag.h

Seagate diagnostic layout header for vendor-specific nvme-cli plugin commands.

Main contents:
- Plugin version constants: Seagate `1.2`, OCP Seagate `1.0`.
- Persistent log and chunk sizes used by diagnostic retrieval.
- `stx_jag_pan_mn`: static list of 123 legacy Jaguar/Panthor model numbers used by `stx_is_jag_pan` to choose legacy log behavior.
- Supported log page map types: `log_page_map_entry` and `log_page_map`, matching a 4 KiB vendor log directory payload.
- Extended SMART types:
  - `SmartVendorSpecific`
  - `EXTENDED_SMART_INFO_T`
  - `vendor_smart_attribute_data`
  - `STX_EXT_SMART_LOG_PAGE_C0`
  - `vendor_log_page_CF`
- Telemetry header `nvme_temetry_log_hdr`, used for host/controller telemetry dumping.
- PCIe error log layout `pcie_error_log_page`.
- Firmware activation history layouts `stx_fw_activ_his_ele` and `stx_fw_activ_history_log_page`.
- Enumerations for Seagate extended SMART attribute indexes and vendor SMART attribute IDs.

Notable role:
- This header is not just declarations; it defines large static data and packed firmware ABI structs. It is coupled tightly to `seagate-nvme.c` parsing/printing logic.
- It declares `seaget_d_raw`, implemented in `seagate-nvme.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-diag.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.c

Seagate vendor-specific nvme-cli plugin implementation. It exposes log discovery, SMART/temperature/PCIe/fw-history reporting, telemetry dumping, clear operations, and plugin version commands.

Key command handlers:
- `log_pages_supp`: retrieves vendor log `0xc5` and prints supported log pages in normal or JSON format.
- `vs_smart_log`: identifies controller model, branches for legacy Jaguar/Panthor devices, reads extended SMART log `0xc4` plus DRAM supercap log `0xcf`, or legacy SMART health log `0xc0`.
- `temp_stats`: combines standard SMART temperature sensors with extended SMART max-temperature attributes and supercap temperature from `0xcf`.
- `vs_pcie_error_log`: reads `0xcb`, computes correctable/uncorrectable totals, and prints detailed PCIe error counters.
- `stx_vs_fw_activate_history`: reads firmware activation history from `0xc2`.
- `clear_fw_activate_history`: for legacy models, sends set-feature `0xc1` with `0x80000000`.
- `vs_clr_pcie_correctable_errs`: clears PCIe counters via feature `0xe1`/log `0xcb` for non-legacy and feature `0xc3` for legacy, then unconditionally sends the `0xe1` clear path again.
- `get_host_tele`: retrieves telemetry host-initiated log `0x07`, optionally with capture bit encoded into the log identifier.
- `get_ctrl_tele`: retrieves telemetry controller-initiated log `0x08`.
- `vs_internal_log`: dumps controller telemetry `0x08` as binary to stdout or a file.
- `seagate_plugin_version` and `stx_ocp_plugin_version`: print plugin version numbers.

Important helpers:
- `log_pages_supp_print`: maps Seagate/OCP/vendor log IDs to human names.
- `stx_is_jag_pan`: checks controller model against the legacy model table in `seagate-diag.h`.
- `smart_attribute_vs`: interprets SMART raw values differently depending on extended SMART version.
- Multiple JSON/human print helpers for SMART, DRAM supercap, C0 health, PCIe errors, and firmware history.
- `seaget_d_raw`: writes binary buffers to a file descriptor.

Notable behavior:
- `vs_smart_log` first branches on legacy model, but then proceeds to retrieve `0xc4`/`0xcf` again after the branch. This means some devices may get duplicate extended SMART output or extra log reads.
- Several JSON paths allocate root objects but not all paths free them consistently.
- `json_stx_vs_fw_activate_history` prints timestamp text to stdout while constructing JSON, causing mixed output.
- Telemetry retrieval reads the header first, then iterates in `TELEMETRY_BLOCKS_TO_READ` chunks of 512-byte blocks using `libnvme_get_log` with log page offset.
- File output in `vs_internal_log` uses `O_WRONLY | O_CREAT` without `O_TRUNC`, so old longer files can retain trailing data.

External dependencies:
- libnvme standard get-log, get-feature, set-feature, identify.
- nvme-cli JSON and hexdump helpers.
- Seagate packed ABI structures from `seagate-diag.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.h

Seagate plugin command registration header. It defines `CMD_INC_FILE` as `plugins/seagate/seagate-nvme` and registers the `seagate` plugin.

Registered commands:
- `vs-temperature-stats`
- `vs-log-page-sup`
- `vs-smart-add-log`
- `vs-pcie-stats`
- `clear-pcie-correctable-errors`
- `get-host-tele`
- `get-ctrl-tele`
- `vs-internal-log`
- `vs-fw-activate-history`
- `clear-fw-activate-history`
- `plugin-version`
- `cloud-SSD-plugin-version`

The header has minor formatting inconsistencies but is otherwise a standard nvme-cli plugin registration file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/meson.build

Meson build fragment for the SED plugin. It adds two source files to `plugin_sources`:
- `plugins/sed/sed.c`
- `plugins/sed/sedopal_cmd.c`

No conditional logic or dependencies are declared here.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sed.c -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/sed.c

CLI wrapper layer for the SED Opal plugin. It parses nvme-cli options, opens the target NVMe namespace device, and delegates to `sedopal_cmd.c` implementation functions.

Commands:
- `sed_opal_discover`: query and display locking features.
- `sed_opal_initialize`: initialize an Opal device for locking.
- `sed_opal_revert`: revert from locking state; supports destructive and PSID flags.
- `sed_opal_lock`: lock the global locking range.
- `sed_opal_unlock`: unlock, optionally read-only.
- `sed_opal_password`: change the locking password.

Important behavior:
- `sed_opal_open_device` requires a namespace handle, not a controller handle. It emits an explicit error if invoked on `/dev/nvmeX` instead of `/dev/nvmeXnY`.
- Option variables are globals declared in `sedopal_cmd.c`; CLI option parsing mutates those globals directly.
- `--ask-key`, `--read-only`, `--destructive`, `--psid`, `--verbose`, and `--udev` control behavior in lower layers.

Storage relevance:
- This plugin manipulates block-layer OPAL locking state, which directly affects namespace accessibility, partition rereads, and mounted filesystem usability.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sed.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sed.h -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/sed.h

SED plugin command registration header. It registers plugin name `sed` with description `SED Opal Command Set`.

Registered commands:
- `discover`
- `initialize`
- `revert`
- `lock`
- `unlock`
- `password`

It includes Linux `sed-opal.h` and uses nvme-cli command-generation macros. `discover` includes an extra `"1"` command metadata argument.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sed.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.c -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.c

SED Opal implementation layer. It uses Linux OPAL ioctls from `linux/sed-opal.h` rather than issuing raw NVMe security commands itself.

Global option state:
- `sedopal_ask_key`
- `sedopal_ask_new_key`
- `sedopal_destructive_revert`
- `sedopal_psid_revert`
- `sedopal_lock_ro`
- `sedopal_discovery_verbose`
- `sedopal_discovery_udev`

Core operations:
- `sedopal_set_key`: either prompts with `getpass` and includes the key in the ioctl payload, or references the kernel keyring when supported.
- `sedopal_cmd_initialize`: checks locking is not already enabled, takes ownership, activates LSP, configures global locking range, and sets password.
- `sedopal_cmd_lock` / `sedopal_cmd_unlock`: call `sedopal_lock_unlock`; unlock rereads partition table with `BLKRRPART`.
- `sedopal_cmd_revert`: supports PSID revert, destructive TPER revert, or preserve-data LSP+TPER revert depending on flags and available ioctl definitions.
- `sedopal_cmd_password`: changes Admin1 password and optionally SID password if `IOC_OPAL_SET_SID_PW` exists.
- `sedopal_cmd_discover`: issues `IOC_OPAL_DISCOVERY`, parses level 0 feature records, prints locking state and optional verbose features.
- `sedopal_locking_state`: returns feature bits from the locking descriptor.

Discovery parsing:
- `sedopal_parse_features` recognizes TPER, locking, geometry, Opal v1/v2, Opalite, Pyrite v1/v2, Ruby, single user mode, datastore, locking LBA, block SID auth, namespace locking, data removal, and namespace geometry.
- Feature printers convert big-endian fields from discovery descriptors and print human-readable capability details.
- `--udev` changes locking output to `DEV_SED_*=` variables suitable for udev rules.

Important safety behavior:
- Destructive and PSID reverts require double interactive confirmation.
- Password length is constrained to 8-32 characters.
- Revert refuses preserve-data operation when the drive is locked.
- Initialization refuses already initialized drives.

Notable issues:
- `sedopal_set_key` compares re-entered password using the first key’s length only; it does not explicitly compare lengths.
- Passwords are copied into ioctl structs and are not scrubbed from memory afterward.
- `sedopal_print_features` defines `sedopal_print_data_removal` but does not call it, so parsed data removal capability is not displayed in verbose output.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.h -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.h

SED Opal command header. It declares prompts, password length limits, global option flags, command enum values, and implementation functions.

Key definitions:
- Password prompts for current, new, re-entered, and PSID inputs.
- `SEDOPAL_MIN_PASSWORD_LEN` 8 and `SEDOPAL_MAX_PASSWORD_LEN` 32.
- `NVME_DEV_PATH` set to `/dev/nvme`, though this file’s listed implementation path does not use an opener by that name.
- `enum sedopal_cmds` for initialize, lock, unlock, revert, password, discover.

Declared APIs:
- Command functions: initialize, lock, unlock, revert, password, discover.
- Utility functions: `sedopal_open_nvme_device`, `sedopal_lock_unlock`, `sedopal_error_to_text`, `sedopal_locking_state`.

Note: `sedopal_open_nvme_device` is declared here but not implemented in the listed `.c` file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_cmd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_spec.h -->
# File Research: sources/virtualization/nvme-cli/plugins/sed/sedopal_spec.h

TCG Opal/Ruby/Pyrite discovery specification layout header.

Main contents:
- `enum sed_status_codes`: method status codes used by `sedopal_error_to_text`.
- Internal feature bitmask constants for parsed feature presence.
- Level 0 discovery feature codes from TCG Opal specifications.
- Locking feature bits: supported, enabled, locked, media encryption, MBR enabled/done.
- Packed discovery structures:
  - `level_0_discovery_header`
  - `level_0_discovery_features`
  - `tper_desc`
  - `locking_desc`
  - `geometry_reporting_desc`
  - `opalv1_desc`
  - `opalv2_desc`
  - `single_user_mode_desc`
  - `datastore_desc`
  - `opalite_desc`
  - `pyrite_v1_desc`
  - `pyrite_v2_desc`
  - `ruby_desc`
  - `locking_lba_desc`
  - `block_sid_auth_desc`
  - `config_ns_desc`
  - `data_removal_desc`
  - `ns_geometry_desc`

Storage relevance:
- These structures describe device encryption/locking capabilities and logical block geometry that can affect namespace and filesystem access policy.
- All multi-byte descriptor fields are big-endian and are converted in `sedopal_cmd.c`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/sed/sedopal_spec.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.c -->
# File Research: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.c

Shannon vendor-specific nvme-cli plugin implementation.

Main commands:
- `get_additional_smart_log`: retrieves vendor log page `0xca`, parses Shannon-specific additional SMART items, and supports normal or raw binary output.
- `get_additional_feature`: wrapper around `nvme_get_features` for Shannon additional feature IDs, notably `0x02` power management.
- `set_additional_feature`: wrapper around `nvme_set_features`, optionally reading a feature payload from file/stdin.
- `shannon_id_ctrl`: delegates to generic `__id_ctrl`.

Key structures:
- `nvme_shannon_smart_log_item`: packed item with normalized value and a 6-byte raw field, with wear-level and thermal-throttle union views.
- `nvme_shannon_smart_log`: fixed array of SMART items indexed by enum values.

Notable details:
- SMART fields mirror common Intel/ScaleFlux-style additional SMART concepts: program/erase fail, wear leveling, E2E/CRC, timed workload, thermal throttle, NAND/host writes, SRAM error.
- `show_shannon_smart_log` appears to print `sram_error_count` using the normalized value from `RETRY_BUFFER_OVERFLOW` but raw value from `SRAM_ERROR_CNT`, likely a copy/paste defect.
- `get_additional_feature` allocates optional returned data but does not print `result` or payload, so it mostly validates and sends the command.
- The registered command name in the header has a typo: `set-additioal-feature`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.h -->
# File Research: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.h

Shannon plugin registration header. It registers plugin name `shannon` with description `Shannon vendor specific extensions`.

Registered commands:
- `smart-log-add`
- `set-additioal-feature`
- `get-additional-feature`
- `id-ctrl`

The misspelling `set-additioal-feature` is part of the command surface and therefore externally visible.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/shannon/shannon-nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/meson.build -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/meson.build

Meson build fragment for the Solidigm plugin. It adds Solidigm plugin sources to `plugin_sources`, including command registration, utility, SMART, garbage collection, latency, log-page directory, telemetry, internal logs, market log, temperature stats, drive info, OCP version, and workload tracker modules.

It also descends into `solidigm-telemetry` with `subdir('solidigm-telemetry')`.

Files from this work item included here:
- `solidigm-garbage-collection.c`
- `solidigm-get-drive-info.c`
- `solidigm-id-ctrl.c`
- `solidigm-internal-logs.c`
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.c

Solidigm vendor garbage collection log command implementation.

Main command:
- `solidigm_get_garbage_collection_log`: opens device, validates output format, gets the Solidigm UUID index via `sldgm_get_uuid_index`, retrieves vendor log ID `0xfd` with UUID index encoded into CDW14, then prints binary, JSON, or text.

Data layout:
- `gc_item`: `timer_type` plus `timestamp`.
- `garbage_control_collection_log`: version fields, 100 GC items, and reserved padding to fill the payload.

Output:
- Text prints device name, UUID index, and all 100 timestamp/timer-type entries.
- JSON emits an array of 100 entries with `timestamp` and `timer_type`.
- Binary dumps the full raw struct.

Dependencies:
- libnvme get-log passthrough.
- Solidigm UUID helper from `solidigm-util.h`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.h

Header declaring the Solidigm garbage collection log command:
- `solidigm_get_garbage_collection_log`

No include guard is present in this small declaration-only header.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-garbage-collection.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.c

Solidigm drive hardware information command implementation.

Main command:
- `sldgm_get_drive_info`: prints FTL unit size in normal or JSON format.

Flow:
- Opens the target with nvme-cli helpers.
- Accepts only normal or JSON output.
- Scans libnvme topology.
- Resolves either a controller’s first namespace or a namespace handle.
- Identifies namespace with `libnvme_ns_identify`.
- Requires `ns.nsfeat & 0x10`, described as performance options availability.
- Finds current LBA format, computes LBA size as `1 << ds`, and computes `FTL_unit_size = (npwg + 1) * lba_size / 1024`.

Output:
- Normal: `FTL_unit_size: <value>`
- JSON: object with `FTL_unit_size`.

Relevance:
- Reports write granularity-like information derived from namespace preferred write granularity and LBA size, useful for alignment/performance decisions above the block layer.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.h

Header declaring:
- `sldgm_get_drive_info`

Small declaration-only Solidigm plugin header without an include guard.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-get-drive-info.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.c

Solidigm vendor-specific Identify Controller formatter.

Main function:
- `sldgm_id_ctrl(uint8_t *vs, struct json_object *root)`

It interprets the vendor-specific identify-controller bytes as `nvme_vu_id_ctrl_field` and prints either text or appends JSON fields.

Parsed fields include:
- Stripe size, health string, link speed, negotiated link width.
- Security capability/status.
- Bootloader string.
- WWID.
- Bandwidth/IO limit granularity strings.
- Signature, version, product type, NAND type, form factor, firmware status.
- P4 revision, customer ID, usage model.
- Command-set bits: ZNS NVMe, MFND NVMe, CDW14-to-CDW13 mapping, VPD availability.

Notable behavior:
- If `health[0]` is empty, it reports `healthy`.
- JSON uses fixed-length string creation for several fields, preserving embedded/trailing bytes up to field width.
- Numeric fields are mostly printed directly; only `ww` is explicitly little-endian converted.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.h

Header for Solidigm Identify Controller vendor-specific formatting.

Includes:
- `<inttypes.h>`
- `util/json.h`

Declares:
- `void sldgm_id_ctrl(uint8_t *vs, struct json_object *root);`

No include guard is present.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-id-ctrl.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.c -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.c

Solidigm internal/debug log collection implementation. It can dump vendor NLOG/event/assert logs, standard telemetry logs, identify pages, persistent event log, and selected standard/vendor log pages into a timestamped directory that is then zipped.

Public command:
- `solidigm_get_internal_log`: parses `--type` and `--dir-name`, creates `<serial>-YYYYMMDDHHMMSS`, collects requested logs, compresses with `zip`, and removes the raw folder on successful compression.

Supported types:
- `ALL`
- `HIT`
- `CIT`
- `NLOG`
- `ASSERT`
- `EVENT`
- `EXTENDED`

Vendor dump path:
- Uses admin passthrough opcode `0xd2`.
- `cmd_dump_repeat` transfers up to 4096 bytes per command, tracks dword offsets in CDW13, and optionally forces max transfer size in CDW10.
- `ilog_dump_nlogs`: iterates selected core and NLOG number, writes `NLog.bin`.
- `ilog_dump_assert_logs`: reads assert header, writes valid core assert sections to `AssertLog.bin`.
- `ilog_dump_event_logs`: reads event header and per-core event sections to `EventLog.bin`.

Standard/extended dump path:
- `ilog_dump_telemetry`: uses Solidigm dynamic telemetry helper for host-initiated or controller-initiated telemetry. It enables extended telemetry data area support through host behavior feature when needed and restores previous host behavior afterward.
- `ilog_dump_identify_pages`: saves controller, namespace, namespace descriptor, CSI, allocated namespace, namespace controller list, active/allocated namespace lists, NVM set list, controller list, etc.
- `ilog_dump_no_lsp_log_pages`: saves many standard and vendor log pages without LSP, including SMART, error, firmware slot, changed namespace, command effects, sanitize, OCP/VU pages, SMART attributes, temperature stats, and latency outlier.
- `ilog_dump_pel`: releases/establishes persistent event log context, reads full PEL, saves it, then releases context.

Important helpers:
- `get_serial_number`: identifies controller and trims trailing spaces in serial.
- `ilog_ensure_dump_id_ctrl`: caches and dumps identify controller once.
- `is_atmos`: detects model prefix `SOLIDIGM SB5`.
- `get_max_da`: chooses telemetry data area based on model and identify-controller LPA bits.
- `log_save`: creates subdirectories and writes full buffers.
- `ensure_dir`: creates subdirectories if missing.

Notable issues:
- `ensure_dir` calls `mkdir(file_path, 777)`, using decimal `777` rather than octal `0777`.
- Shell commands are assembled for `zip` and `rm -rf`; `zip` command quotes paths, but cleanup command does not quote `cfg.out_dir`.
- `ilog_dump_pel` calls `nvme_get_log_persistent_event` with `pevent == NULL` before allocation, then allocates and repeats; this first call is suspicious.
- `ilog_dump_log_page` ignores its `nsid` parameter and passes namespace ID `0` to `nvme_get_nsid_log`.
- `cmd_dump_repeat` treats short positive `write` counts as success and does not retry partial writes.
- The code continues after many collection failures and reports total successful files, which is appropriate for best-effort debug collection but means command success can mask missing log classes.

Storage relevance:
- Captures the diagnostic state needed for NVMe device failure analysis, including controller/namespace identify data, persistent event logs, telemetry, and vendor firmware logs. These artifacts are important when correlating filesystem/block-layer failures with drive firmware or media state.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.h -->
# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.h

Header declaring:
- `solidigm_get_internal_log`

Small declaration-only header for the Solidigm internal log collection command. No include guard is present.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-internal-logs.h -->