# Group Research: group_1325_nvme_cli_sources_virtualization_nvme_cli_libnvme_src_nvme_nbft_c_so_911279a49311

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/nvme-cli` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.c

This file implements libnvme’s NBFT reader/parser for raw ACPI NVMe Boot Firmware Table data. Its public entry points are `libnvmf_read_nbft()` and `libnvmf_free_nbft()`.

Core behavior:
- Reads a binary NBFT file into memory, stores filename/raw bytes in `struct libnbft_info`, then parses table contents.
- Validates table shape before interpretation: minimum size, checksum, `"NBFT"` signature, revision `1.0`, header length, heap bounds, and descriptor IDs.
- Converts raw NBFT descriptors into higher-level libnvme structures: host, HFI, discovery, security list placeholder, and subsystem namespace entries.
- Resolves cross-descriptor references by descriptor index for HFI, discovery, and security associations.

Important implementation details:
- `csum()` validates ACPI checksum by summing all bytes.
- `format_ip_addr()` treats NBFT 16-byte addresses as IPv6 unless they are IPv4-mapped IPv6.
- `in_heap()` and `__get_heap_obj()` validate heap object offset/length before returning pointers into the raw NBFT buffer.
- Heap string validation checks NUL termination and logs debug messages for short or unterminated strings.
- `read_hfi_info_tcp()` parses TCP-specific HFI transport data, including PCI SBDF, MAC, VLAN, IPs, DNS, DHCP server, route metric, host name, default-route flag, and DHCP override flag.
- `read_ssns()` builds namespace entries, including transport address/service ID, NSID/NID, digest requirements, unavailable/discovered flags, discovery/security links, primary and secondary HFI list, subsystem NQN, and optional extended information.
- `read_ssns_exended_info()` handles optional SSNS extended info, including ASQSZ, controller ID, and DHCP root path.

Notable limitations and risks:
- `read_security()` is currently unimplemented and always returns `-EINVAL`, so `security_list` remains effectively empty even when NBFT contains security descriptors.
- Descriptor-list allocator calls use `sizeof(struct libnbft_hfi)`-style element sizes where the target arrays hold pointers; this over-allocates, which is safe but imprecise.
- `read_ssns()` frees `ssns` on failure but does not separately free `ssns->hfis` if allocation succeeded before a later failure.
- Most parsed string/IP pointers point into `raw_nbft`; the lifetime is tied to `libnbft_info`.
- Several parse failures for optional cross-references are debug logged rather than fatal, allowing partially linked NBFT models.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.h

This header defines libnvme’s public parsed NBFT object model and the NBFT read/free APIs.

Key data structures:
- `enum libnbft_primary_admin_host_flag`: primary administrative host priority states.
- `struct libnbft_host`: raw host UUID pointer, host NQN, configured flags, and primary-host flag.
- `struct libnbft_hfi_info_tcp`: TCP HFI details such as PCI SBDF, MAC, VLAN, IP origin, IP/gateway/DNS/DHCP addresses, route metric, host name, default route flag, and DHCP override flag.
- `struct libnbft_hfi`: HFI index, transport string, and TCP-specific info.
- `struct libnbft_discovery`: discovery descriptor index plus optional security/HFI links and discovery URI/NQN.
- `struct libnbft_security`: currently only an index field with a TODO for future fields.
- `enum libnbft_nid_type`: namespace identifier type values for none, EUI64, NGUID, and namespace UUID.
- `struct libnbft_subsystem_ns`: parsed SSNS data, including descriptor links, HFI list, transport address/service, namespace identifiers, digest flags, extended-info fields, discovered/unavailable flags.
- `struct libnbft_info`: top-level parsed NBFT containing filename, raw bytes, host, and null-terminated descriptor lists.
- `struct nbft_file_entry`: linked-list wrapper for collections of parsed NBFT files.

Public API:
- `libnvmf_read_nbft(ctx, &nbft, filename)` reads and parses a raw ACPI NBFT file.
- `libnvmf_free_nbft(ctx, nbft)` releases parsed lists, raw buffer, filename, and the top-level object.

Important ownership detail:
- Many string and ID fields are pointers into `raw_nbft`, not independent allocations. Consumers must not outlive or mutate the owning `struct libnbft_info`.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nbft.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-crypto.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-crypto.c

This is the no-crypto build fallback for libnvme. It provides ABI-compatible definitions for crypto, TLS key, DH-HMAC-CHAP key, host ID, and host NQN helpers when crypto/keyring support is not compiled in.

Behavior:
- Operational functions return `-ENOTSUP`.
- String-returning helpers return `NULL`.
- It covers TLS key export/import, keyring read/lookup/update/revoke/scan, TLS key identity generation/insertion, DHCHAP key generation, raw secret creation, host ID generation, host NQN generation, and host config file reads.

Role in the build:
- Allows callers to link against the same symbol set even in minimal builds.
- Makes unsupported crypto behavior explicit through standard negative errno values rather than compile-time missing symbols.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-fabrics.c

This is the no-fabrics fallback translation unit for builds without full NVMe-oF support.

Provided behavior:
- `traddr_is_hostname()` always returns `false`.
- `libnvmf_default_config()` is a no-op.
- `libnvmf_read_sysfs_fabrics_attrs()` is a no-op.
- `libnvme_ctrl_find()` has a limited non-Windows implementation: it iterates controllers in a subsystem and matches transport and optional transport address, then returns the first match. On Windows or no match it returns `NULL`.

Role:
- Preserves parts of the library interface in configurations where fabrics support is disabled.
- Keeps controller lookup minimally useful for existing in-memory topology objects, but omits fabrics-specific defaulting and sysfs population.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-json.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-json.c

This is the no-JSON fallback for libnvme configuration/tree serialization functions.

Functions:
- `json_read_config()`
- `json_update_config()`
- `json_dump_tree()`

All three return `-ENOTSUP`.

Role:
- Keeps callers linkable when JSON support is not built.
- Clearly reports that config read/update and tree dump JSON operations are unsupported in this build.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-json.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-mi.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-mi.c

This is the no-NVMe-MI fallback for builds without Management Interface support.

Provided behavior:
- `libnvme_mi_status_to_string()` returns `"MI support disabled"`.
- MI transport open/init and MI admin passthrough return `-ENOTSUP`.
- MI transport close is a no-op.

Role:
- Maintains MI-related symbols for ABI/link compatibility.
- Gives callers a deterministic unsupported status when MI transport handling is disabled.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-mi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-uring.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-uring.c

This file provides fallback implementations when io_uring support is not available.

Behavior:
- `libnvme_open_uring()` returns `-ENOTSUP`.
- `libnvme_close_uring()` is a no-op.
- `__libnvme_transport_handle_open_uring()` marks the handle state as `LIBNVME_IO_URING_STATE_NOT_AVAILABLE` and returns `-ENOTSUP`.
- Async admin and I/O passthrough submission functions attempt to transition unknown state once, then return `-ENOTSUP`.
- Reap and wait functions return `-ENOTSUP`.

Role:
- Lets higher-level code probe async support and fall back to synchronous paths.
- Avoids missing symbols while preserving a clear state machine value for “not available”.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/no-uring.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-base.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-base.h

This is the central inline command-construction header for NVMe base specification admin commands plus common command-set fields. It does not submit commands; it fills `struct libnvme_passthru_cmd` objects consistently for later execution.

Major contents:
- Field shift/mask definitions for Get Log Page, Identify, Set/Get Features, Namespace Management, Firmware Commit/Download, Namespace Attach, Directives, Device Self-test, Virtualization Management, Capacity Management, Lockdown, Format NVM, Security Send/Receive, Sanitize, Get LBA Status, common I/O fields, NVM fields, ZNS fields, and MI flags.
- `NVME_FIELD_ENCODE()` fallback macro.
- Static inline initializers for many admin command families.

Get Log helpers:
- Base `nvme_init_get_log()` plus specialized helpers for supported log pages, error, SMART, firmware slot, changed namespaces, command effects, device self-test, telemetry host/controller, endurance group, predictable latency, ANA, persistent event, LBA status, media unit status, supported capacity configs, feature effects, lockdown, boot partition, rotational media, dispersed namespace, management address, power measurement, PHY RX EOM, reachability groups/associations, changed allocated namespaces, and FDP logs/events.

Identify helpers:
- Base `nvme_init_identify()` plus namespace/controller variants, namespace descriptor list, NVM set list, CSI namespace/controller/active namespace list, independent namespace identity, namespace user data formats, allocated namespace list/namespace, namespace controller list, controller list, primary/secondary controller capabilities, namespace granularity, UUID list, domain list, endurance group list, CSI allocated namespace list, CSI namespace data, and command-set structure.

Feature helpers:
- Base `nvme_init_set_features()` and `nvme_init_get_features()`.
- Specialized set/get helpers for arbitration, power management, LBA range, temperature threshold, error recovery, volatile write cache, IRQ coalescing/config, write atomic, async event configuration, APST, timestamp, HCTM, non-operational power state config, read recovery level, predictable latency config/window, LBA status interval, host behavior, sanitize, endurance event config, software progress, host ID, reservation notification mask/persistence, write protection, I/O command set profile, and live-migration controller data queue feature.

Other admin helpers:
- Namespace management create/delete.
- Firmware commit/download, with firmware download validating nonzero DWord-aligned length and offset.
- Device self-test.
- Namespace attach/detach.
- Directive send/receive and directive-specific identify/streams helpers, including stream status entry-count validation.
- Virtualization resource management.
- Capacity management.
- Discovery Information Management send.
- Lockdown.
- Live Migration helpers for track send, migration send/receive, controller data queue create/delete.
- Format NVM, Security Send/Receive, Sanitize NVM/namespace, Get LBA Status.
- Controller list initialization helper converts controller IDs to little endian.

Important patterns:
- Every initializer zeroes the passthrough command before assigning opcode, namespace ID, command dwords, data length, metadata length, and user-space pointers.
- DWord fields are encoded through named shift/mask constants rather than open-coded bit shifts.
- Payload pointer fields are stored as integer-cast user addresses in `cmd->addr` and `cmd->metadata`.
- Endianness conversion is applied where payload structures are constructed, such as controller lists.

Risk/edge considerations:
- These helpers generally trust caller-provided buffers and semantic validity; most validation is limited to cases like firmware DWord alignment and directive stream entry limits.
- They are static inline API surface, so behavior changes affect every caller at compile time.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-base.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-fabrics.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-fabrics.h

This header adds NVMe over Fabrics-specific command initializers on top of the base command helpers.

Log helpers:
- `nvme_init_get_log_discovery()` initializes Discovery Log retrieval with an explicit log page offset.
- `nvme_init_get_log_host_discovery()` initializes Host Discovery log retrieval and encodes the all-host-entries flag in LSP.
- `nvme_init_get_log_ave_discovery()` initializes AVE Discovery log retrieval.
- `nvme_init_get_log_pull_model_ddc_req()` initializes Pull Model DDC Request log retrieval.

Property helpers:
- `nvme_init_set_property()` constructs Fabrics Set Property commands using `nvme_admin_fabrics`, setting the fabrics command type in `nsid`, 32/64-bit register flag in `cdw10`, property offset in `cdw11`, and value split across `cdw12/cdw13`.
- `nvme_init_get_property()` constructs Fabrics Get Property commands similarly, without a payload value.

Role:
- Centralizes NVMe-oF property and discovery command dword layout.
- Depends on base `nvme_init_get_log()` and fabric type/register helpers from the NVMe type headers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-mi.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-mi.h

This header contains small NVMe Management Interface command helpers.

Contents:
- `nvme_init_get_log_mi_cmd_supported_effects()` initializes Get Log Page for MI Commands Supported and Effects.
- `nvme_init_mi_cmd_flags()` encodes the MI Ignore Shutdown flag into `cmd->flags`.

Role:
- Provides MI-specific setup while reusing base Get Log infrastructure.
- Keeps MI command flag encoding in one place via `NVME_MI_ADMIN_CFLAGS_ISH_*` constants defined in the base command header.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-mi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-nvm.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-nvm.h

This header defines inline initializers for NVM Command Set I/O commands and related helper payload constructors.

Command initializers:
- `nvme_init_flush()` for Flush.
- `nvme_init_io()` generic NVM I/O initializer that sets opcode, namespace, SLBA dwords, data and metadata pointers/lengths.
- `nvme_init_write()`, `nvme_init_read()`, `nvme_init_write_uncorrectable()`, `nvme_init_compare()`, `nvme_init_write_zeros()`, and `nvme_init_verify()`.
- `nvme_init_dsm()` for Dataset Management.
- Reservation helpers: register, report, acquire, release.
- I/O Management Receive/Send helpers and FDP-specific wrappers for reclaim unit handle status/update.
- `nvme_init_copy()` for Copy, selecting descriptor payload length by descriptor format.

Payload/helper constructors:
- `nvme_init_app_tag()` sets application tag and mask fields in `cdw15`.
- `nvme_init_dsm_range()` fills DSM range arrays with little-endian fields.
- `nvme_init_copy_range_f0/f1/f2/f3()` fills Copy descriptors, including endian conversion and zeroing where extended reference-tag arrays require it.
- `nvme_init_var_size_tags()` encodes variable-sized protection/storage tags into `cdw2`, `cdw3`, and `cdw14` for different protection information formats.

Important patterns:
- I/O helpers compose around `nvme_init_io()` to avoid repeating opcode/namespace/address/SLBA setup.
- Command-specific dword fields use constants from `nvme-cmds-base.h`.
- Payload helper functions convert host-native inputs into the endian layout expected by NVMe command payload structures.

Risk/edge considerations:
- Most helpers do not validate that sizes match namespace LBA format or metadata requirements.
- `nvme_init_fdp_reclaim_unit_handle_update()` computes `npids - 1`; callers must avoid passing zero placement IDs.
- Variable-sized tag setup returns `-EINVAL` for unknown protection information formats and must be checked by callers.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-nvm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-zns.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-zns.h

This header provides Zoned Namespace Command Set command initializers.

Contents:
- `nvme_init_get_log_zns_changed_zones()` initializes retrieval of the ZNS Changed Zones log.
- `nvme_init_zns_identify_ns()` initializes ZNS-specific Identify Namespace.
- `nvme_init_zns_identify_ctrl()` initializes ZNS-specific Identify Controller.
- `nvme_init_zns_mgmt_send()` constructs Zone Management Send commands, including SLBA, action, select-all flag, action-specific option, management field, and optional payload.
- `nvme_init_zns_mgmt_recv()` constructs Zone Management Receive commands, including SLBA, action, action-specific field/features, transfer length, and payload.
- `nvme_init_zns_report_zones()` wraps management receive for regular or extended report zones, with partial report support.
- `nvme_init_zns_append()` constructs Zone Append I/O commands with data/metadata pointers, ZSLBA, NLB, control, directive-specific field, and optional command extension value.

Role:
- Keeps ZNS command setup separate from base and NVM command helpers while sharing common field definitions.
- Encodes the ZNS command set identifier where Identify/Get Log require CSI selection.

Risk/edge considerations:
- Helpers assume caller-provided lengths are valid DWord-compatible transfer sizes where the spec requires that.
- Zone Append only encodes `cev` when the control field indicates a command extension type.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-zns.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.c

This file implements non-inline libnvme command helper routines that execute or coordinate multi-step command flows.

Initialization and transfer behavior:
- A constructor reads `LIBNVME_FORCE_4K`; values `1`, `true`, or strings beginning with `enable` force log transfers to 4 KiB chunks.
- `submit_get_log_cmd()` prefers async admin passthrough via io_uring unless unavailable or returning `-ENOTSUP`, then falls back to synchronous admin passthrough.
- `wait_get_log_cmd()` waits only when io_uring is available.
- `libnvme_get_log()` splits a requested log transfer into chunks, updates LPO/NUMD fields for each chunk, retains asynchronous events for all intermediate chunks, and waits after the final submission.

ANA log handling:
- `read_ana_chunk()` reads enough chunks to cover a requested pointer range.
- `try_read_ana()` walks ANA group descriptors without dereferencing potentially misaligned structures; it uses `memcpy()` for `nnsids`.
- `libnvme_get_ana_log_atomic()` retries ANA reads and compares `chgcnt` to ensure multi-command reads are atomic. It reports the actual length read and returns `-EAGAIN` if the log changes across all retries.

Feature helpers:
- `libnvme_set_etdas()` and `libnvme_clear_etdas()` read Host Behavior, set/clear the ETDAS bit if needed, and report whether a change was made.

Identify/log utilities:
- `libnvme_get_uuid_list()` identifies the controller first and only requests the UUID list if controller attributes indicate support.
- `libnvme_get_telemetry_max()` identifies controller telemetry capabilities and transfer limits.
- `libnvme_get_telemetry_log()` retrieves telemetry header, calculates full data area size, reallocates, then retrieves the full host/controller telemetry log.
- `libnvme_get_ctrl_telemetry()`, `libnvme_get_host_telemetry()`, and `libnvme_get_new_host_telemetry()` wrap telemetry retrieval with capability checking.
- `libnvme_get_lba_status_log()` reads the LBA status log header first, then reallocates and retrieves the full log if a nonzero page length is reported.
- `libnvme_get_ana_log_len_from_id_ctrl()` and `libnvme_get_ana_log_len()` compute maximum ANA log size from identify controller data.
- `libnvme_get_logical_block_size()` identifies a namespace and returns the active LBA data size as `1 << ds`.

Length helpers:
- `libnvme_get_feature_length()` maps feature IDs and direction/cdw11 details to required payload sizes.
- `libnvme_get_directive_receive_length()` maps directive type/operation pairs to expected receive payload lengths.

Notable issue:
- In `libnvme_get_lba_status_log()`, the first `nvme_init_get_log_lba_status(&cmd, 0, log, sizeof(*buf))` passes `log` instead of `buf` as the data buffer. Since `log` is a pointer-to-pointer parameter, this appears inconsistent with the allocated `buf` and likely prevents the header read from filling the intended buffer.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.h

This is the umbrella public command header. It includes the command type headers and declares the non-inline helper APIs implemented in `nvme-cmds.c`.

Includes:
- `nvme/ioctl.h`
- `nvme/nvme-types.h`
- `nvme/nvme-cmds-base.h`
- `nvme/nvme-cmds-fabrics.h`
- `nvme/nvme-cmds-mi.h`
- `nvme/nvme-cmds-nvm.h`
- `nvme/nvme-cmds-zns.h`

Macros:
- Defines `NVME_FIELD_ENCODE(value, shift, mask)`.
- Defines `NVME_FIELD_DECODE(value, shift, mask)`.

Declared APIs:
- `libnvme_get_log()`
- `libnvme_set_etdas()`
- `libnvme_clear_etdas()`
- `libnvme_get_uuid_list()`
- Telemetry helpers: max, generic telemetry log, controller telemetry, host telemetry, new host telemetry.
- ANA helpers: max length from identify controller, atomic ANA log retrieval, current ANA log length.
- `libnvme_get_logical_block_size()`
- `libnvme_get_lba_status_log()`
- `libnvme_get_feature_length()`
- `libnvme_get_directive_receive_length()`

Role:
- Preserves backward-compatible access to all command initializer families through one include.
- Documents runtime helper semantics and return conventions for command status versus negative errno-style errors.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds.h -->