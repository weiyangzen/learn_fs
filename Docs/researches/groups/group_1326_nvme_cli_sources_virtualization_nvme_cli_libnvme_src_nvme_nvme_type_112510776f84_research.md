# Group Research: group_1326_nvme_cli_sources_virtualization_nvme_cli_libnvme_src_nvme_nvme_type_112510776f84

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-fabrics.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-fabrics.h

## Role

Defines libnvme's public NVMe over Fabrics wire-format types. It is a specification mirror for discovery logs, transport addressing, Discovery Information Management, connect command data, host discovery logs, and AVE discovery records.

## Key Content

- Declares fabrics constants such as `NVME_DISC_SUBSYS_NAME`, default RDMA/discovery ports, `NVMF_NQN_SIZE`, and `NVMF_TRSVCID_SIZE`.
- Defines discovery identity and entry flags:
  - `enum nvme_subsys_type`
  - `enum nvmf_disc_eflags`
  - `struct nvmf_disc_log_entry`
  - `struct nvmf_discovery_log`
- Defines transport-specific address subtype data through `union nvmf_tsas`, with RDMA and TCP views.
- Defines transport/address/security enums:
  - `enum nvmf_trtype`
  - `enum nvmf_addr_family`
  - `enum nvmf_treq`
  - `enum nvmf_rdma_qptype`
  - `enum nvmf_rdma_prtype`
  - `enum nvmf_rdma_cms`
  - `enum nvmf_tcp_sectype`
- Provides bit extraction macros using `NVMF_GET`, including `NVMF_TREQ_SECTYPE()` and `NVMF_TREQ_DISABLE_SQFLOW_BIT()`.
- Models Discovery Information Management:
  - `enum nvmf_dim_tas`
  - `enum nvmf_dim_entfmt`
  - `enum nvmf_dim_etype`
  - `enum nvmf_exattype`
  - `struct nvmf_ext_attr`
  - `struct nvmf_ext_die`
  - `union nvmf_die`
  - `struct nvmf_dim_data`
- Models connect and extended discovery payloads:
  - `struct nvmf_connect_data`
  - `struct nvme_host_ext_discover_log`
  - `struct nvme_host_discover_log`
  - `struct nvme_ave_tr_record`
  - `struct nvme_ave_discover_log_entry`
  - `struct nvme_ave_discover_log`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses Linux-style endian and fixed-width aliases such as `__u8`, `__le16`, and `__le64`.
- Relies on shared size constants such as `NVME_NQN_LENGTH`, `NVMF_TSAS_SIZE`, and `NVMF_TRADDR_SIZE`.

## Research Notes

This file is data-only and has no executable logic beyond field extraction macros. The main correctness concern is ABI/layout fidelity: users parse controller-returned discovery data directly into these structs. Variable-length structures such as `struct nvmf_ext_attr`, `struct nvmf_ext_die`, `union nvmf_die`, host discovery logs, and AVE discovery logs require callers to validate total lengths before walking flexible arrays.

## Filesystem/Storage Relevance

This is central to NVMe-oF discovery, which is how remote NVMe block devices are enumerated before being attached to the Linux block layer. It does not implement filesystem logic, but it defines the discovery metadata needed for virtualized and fabric-attached block storage.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-mi.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-mi.h

## Role

Defines public NVMe Management Interface data structures and enums. It is a specification-facing header for MI command effects, port/controller information, subsystem health, controller health, and VPD records.

## Key Content

- Defines MI command supported/effects flags through `enum nvme_mi_cmd_supported_effects` and `NVME_MI_CMD_SUPPORTED_EFFECTS_SCOPE()`.
- Defines the MI command effects log:
  - `struct nvme_mi_cmd_supported_effects_log`
- Models MI read data structures:
  - `struct nvme_mi_read_nvm_ss_info`
  - `struct nvme_mi_port_pcie`
  - `struct nvme_mi_port_smb`
  - `struct nvme_mi_read_port_info`
  - `struct nvme_mi_read_ctrl_info`
  - `struct nvme_mi_osc`
  - `struct nvme_mi_read_sc_list`
- Defines subsystem and SMART warning bit fields:
  - `enum nvme_mi_nss`
  - `enum nvme_mi_sw`
  - extraction macros such as `NVME_MI_NSS_NRDY()` and `NVME_MI_SW_RO()`
- Models health data:
  - `struct nvme_mi_nvm_ss_health_status`
  - `enum nvme_mi_ccs`
  - `struct nvme_mi_ctrl_health_status`
  - `enum nvme_mi_csts`
  - `enum nvme_mi_cwarn`
- Models Vital Product Data:
  - `struct nvme_mi_vpd_mra`
  - `struct nvme_mi_vpd_ppmra`
  - `struct nvme_mi_vpd_telem`
  - `enum nvme_mi_elem`
  - `struct nvme_mi_vpd_tra`
  - `struct nvme_mi_vpd_mr_common`
  - `struct nvme_mi_vpd_hdr`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses shared constants such as `NVME_LOG_MI_CMD_SUPPORTED_EFFECTS_MAX` and `NVME_LOG_MI_CMD_SUPPORTED_EFFECTS_RESERVED`.
- Depends on endian-tagged aliases for wire-format fields.

## Research Notes

The file has no behavior; it provides stable type definitions for MI clients and transports. Several structures include flexible or zero-length arrays, including `nvme_mi_read_sc_list`, `nvme_mi_vpd_telem`, `nvme_mi_vpd_tra`, and `nvme_mi_vpd_hdr`. Callers must handle descriptor lengths carefully when parsing device-provided VPD or command-list payloads.

## Filesystem/Storage Relevance

MI supports out-of-band management of NVMe devices, including health and topology discovery. This helps inventory and diagnose storage devices that may later expose namespaces to the OS block layer.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-mi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nbft.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nbft.h

## Role

Defines ACPI NVMe Boot Firmware Table types for NVMe-oF boot configuration. The structures describe firmware-provided pre-OS boot state for NVMe/TCP interfaces, namespaces, security settings, and discovery controllers.

## Key Content

- Defines NBFT descriptor IDs in `enum nbft_desc_type`, including header, control, host, HFI, SSNS, security, discovery, HFI transport info, SSNS extended info, and HFI extended info.
- Defines NBFT transport type `NBFT_TRTYPE_TCP` and table signature `NBFT_HEADER_SIG`.
- Defines heap object references with `struct nbft_heap_obj`, used throughout the table to point at variable-length heap strings or descriptor objects.
- Models the ACPI-style table header:
  - `struct nbft_header`
- Models control-plane descriptor placement:
  - `struct nbft_control`
  - `enum nbft_control_flags`
- Models host identity:
  - `struct nbft_host`
  - `enum nbft_host_flags`
- Models host fabric interfaces:
  - `struct nbft_hfi`
  - `enum nbft_hfi_flags`
  - `struct nbft_hfi_info_tcp`
  - `enum nbft_hfi_info_tcp_flags`
- Models subsystem namespace boot targets:
  - `struct nbft_ssns`
  - `enum nbft_ssns_flags`
  - `enum nbft_ssns_trflags`
  - `struct nbft_ssns_ext_info`
  - `enum nbft_ssns_ext_info_flags`
- Models security policy:
  - `struct nbft_security`
  - `enum nbft_security_flags`
  - `enum nbft_security_secret_type`
- Models discovery controllers:
  - `struct nbft_discovery`
  - `enum nbft_discovery_flags`

## Dependencies

- Includes `nvme/lib-types.h`.
- Uses `__attribute__((packed))` for structures where firmware table byte layout must not include compiler padding.
- Uses endian-tagged integer aliases for ACPI/NBFT serialized fields.

## Research Notes

This header is pure layout definition. Its important design pattern is indirection through `struct nbft_heap_obj`, where fixed descriptors point into a heap area. Consumers must validate table length, heap bounds, descriptor counts, descriptor lengths, and checksum before trusting offsets. Several flags encode policy state, not merely capabilities, for example administratively configured host identity, DHCP overrides, secure-channel requirements, and namespace availability hints.

## Filesystem/Storage Relevance

NBFT is relevant to boot-from-fabric systems: it tells the OS how firmware connected to NVMe/TCP boot storage and how to rediscover or reestablish that connection. This sits below filesystems, but it directly affects root-device discovery in virtualized or network-boot storage environments.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nbft.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nvm.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nvm.h

## Role

Defines public NVM Command Set structures, flags, and command data payloads. This is the core header for namespace identification, reservation status, Flexible Data Placement, Dataset Management, Copy command descriptors, and I/O management command fields.

## Key Content

- Defines extended LBA/protection metadata fields:
  - `enum nvme_nvm_id_ns_elbaf`
  - `enum nvme_nvm_id_ns_pif`
  - `enum nvme_nvm_id_ns_lbstm`
  - `enum nvme_nvm_id_ns_pic`
  - `enum nvme_nvm_id_ns_pifa`
  - `struct nvme_nvm_id_ns`
- Defines Identify I/O Command Set capabilities:
  - `enum nvme_id_iocs_iocsc`
- Defines reservation notification log structures and event types:
  - `struct nvme_resv_notification_log`
  - `enum nvme_resv_notify_rnlpt`
- Defines Flexible Data Placement support:
  - `enum nvme_fdp_ruh_type`
  - `struct nvme_fdp_ruh_desc`
  - `enum nvme_fdp_config_fdpa`
  - `struct nvme_fdp_config_desc`
  - `struct nvme_fdp_config_log`
  - `enum nvme_fdp_ruha`
  - `struct nvme_fdp_ruhu_desc`
  - `struct nvme_fdp_ruhu_log`
  - `struct nvme_fdp_stats_log`
  - FDP event enums and event payload structs
  - `struct nvme_fdp_ruh_status_desc`
  - `struct nvme_fdp_ruh_status`
- Defines DSM and Copy command payloads:
  - `struct nvme_dsm_range`
  - `struct nvme_copy_range_f0`
  - `struct nvme_copy_range_f1`
  - `struct nvme_copy_range_f2`
  - `struct nvme_copy_range_f3`
  - `enum nvme_copy_range_sopt`
- Defines reservation status and reservation command constants:
  - `struct nvme_registered_ctrl`
  - `struct nvme_registered_ctrl_ext`
  - `struct nvme_resv_status`
  - `enum nvme_feat_resv_notify_flags`
  - `enum nvme_resv_rtype`
  - `enum nvme_resv_racqa`
  - `enum nvme_resv_rrega`
  - `enum nvme_resv_cptpl`
  - `enum nvme_resv_rrela`
- Defines I/O flags and I/O management operation selectors:
  - `enum nvme_io_control_flags`
  - `enum nvme_io_dsm_flags`
  - `enum nvme_dsm_attributes`
  - `enum nvme_io_mgmt_recv_mo`
  - `enum nvme_io_mgmt_send_mo`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses base types such as `struct nvme_timestamp`.
- Uses both little-endian and big-endian fields where the NVMe command set requires them.

## Research Notes

The file is layout-heavy and behavior-free. Many structures represent controller-returned variable-length logs, such as FDP configuration logs and RUH status, and must be walked using descriptor counts and sizes rather than fixed assumptions. Copy descriptors are split by format because protection information and cross-namespace source details differ by command format.

## Filesystem/Storage Relevance

This file describes the command set that block devices expose to higher layers. DSM/deallocate, copy, reservations, write-zeroes related flags, protection information, and FDP all affect how filesystems and storage stacks can optimize placement, discard, copy-offload, and shared-device coordination.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-nvm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-zns.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-zns.h

## Role

Defines public Zoned Namespace Command Set structures and enums. These types describe ZNS identify data, changed zone logs, zone descriptors, zone reports, and zone management command selectors.

## Key Content

- Defines LBA format extension data:
  - `struct nvme_zns_lbafe`
- Defines ZNS identify namespace/controller structures:
  - `struct nvme_zns_id_ns`
  - `struct nvme_zns_id_ctrl`
- Defines changed zone log format:
  - `struct nvme_zns_changed_zone_log`
- Defines zone descriptor type, attributes, and state:
  - `enum nvme_zns_zt`
  - `enum nvme_zns_za`
  - `enum nvme_zns_zs`
  - `struct nvme_zns_desc`
- Defines report zones payload:
  - `struct nvme_zone_report`
- Defines zone management send/receive selectors:
  - `enum nvme_zns_send_action`
  - `enum nvme_zns_recv_action`
  - `enum nvme_zns_report_options`

## Dependencies

- Includes `nvme/types.h` and `nvme/nvme-types-base.h`.
- Uses constants such as `NVME_ZNS_CHANGED_ZONES_MAX`.
- Uses endian-tagged fields for controller wire data.

## Research Notes

The structures directly mirror ZNS specification data. `struct nvme_zone_report` has a flexible `entries[]` array, so callers must size buffers according to requested report length and returned zone count. Zone states and report filters are explicit enum values, making the header the canonical mapping from numeric command fields to libnvme names.

## Filesystem/Storage Relevance

ZNS affects filesystem and block allocation strategy because writes must respect zone state and write-pointer constraints. This file supplies the user-space type definitions needed by tools that inspect and manage zoned NVMe namespaces.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types-zns.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types.h

## Role

Umbrella public header for libnvme NVMe type definitions.

## Key Content

Includes the family of NVMe type headers:

- `nvme/nvme-types-base.h`
- `nvme/nvme-types-fabrics.h`
- `nvme/nvme-types-mi.h`
- `nvme/nvme-types-nvm.h`
- `nvme/nvme-types-zns.h`

## Dependencies

This header has no declarations of its own besides `#pragma once` and include directives.

## Research Notes

This is a convenience aggregation point. Consumers can include it when they need broad NVMe type coverage rather than individual command-set or transport headers.

## Filesystem/Storage Relevance

Indirect relevance: it centralizes access to NVMe storage type definitions used by tooling that interacts with block devices and NVMe-oF environments.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-types.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private-fabrics.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private-fabrics.h

## Role

Internal NVMe-oF private header. It defines fabrics-layer context, hooks, discovery argument state, URI parsing state, extended attribute helpers, interface-address helpers, and controller matching declarations.

## Key Content

- Defines `struct libnvmf_hooks`, a callback table for:
  - retry decisions
  - successful connection notification
  - already-connected notification
  - discovery log handling
  - parser lifecycle and line iteration
- Defines `struct libnvmf_context`, which owns:
  - global libnvme context pointer
  - fabrics hooks
  - controller parameters
  - discovery retry/keep-alive defaults
  - persistent/device selection
  - host identity
  - authentication and TLS/keyring configuration
- Defines `struct libnvmf_discovery_args` with generated accessor/lifecycle annotations.
- Defines `struct libnvmf_uri` for parsed URI components: scheme, protocol, userinfo, host, port, path segments, query, and fragment.
- Provides inline helpers:
  - `libnvmf_exat_len()`
  - `libnvmf_exat_size()`
- Declares cached network interface access with `libnvmf_getifaddrs()` when network support is enabled.
- Defines `struct candidate_args` and `ctrl_match_t`, used by controller reuse/matching logic.
- Declares fabrics matching and entity helpers:
  - `libnvmf_ctrl_match_config()`
  - `libnvmf_ctrl_find()`
  - `libnvmf_get_entity_name()`
  - `libnvmf_get_entity_version()`

## Dependencies

- Includes `ifaddrs.h` when `NVME_HAVE_NETDB` or `CONFIG_FABRICS` is defined.
- Includes public `nvme/fabrics.h`, `nvme/tree.h`, and internal `nvme/private.h`.
- Uses `round_up()` from `private.h` for extended attribute sizing.

## Research Notes

This file separates fabrics-specific internals from the general private header so PCIe-only builds can omit fabrics accessors and code paths. The annotations such as `!generate-accessors` and `!access` indicate that code generation is part of the libnvme internal API maintenance process.

## Filesystem/Storage Relevance

This header supports discovery and connection to remote NVMe block devices. The matching helpers are important for avoiding duplicate fabric controller connections, which affects how remote storage appears in the OS topology.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private-fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private-mi.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private-mi.h

## Role

Internal NVMe Management Interface header. It defines MI request/response containers, endpoint state, transport operations, AEM state, MCTP test injection hooks, and MI transport-handle bridge declarations.

## Key Content

Under `CONFIG_MI`, defines:

- `struct libnvme_mi_req` and `struct libnvme_mi_resp`, wrapping MI headers, payload pointers, lengths, and MIC values.
- `struct libnvme_mi_aem_ctx`, holding asynchronous event occurrence list traversal state and callbacks.
- `struct libnvme_mi_ep`, representing an MI endpoint:
  - global context
  - transport driver
  - transport-private data
  - controller list
  - timeout/MPRT/quirk state
  - command set identifier
  - inter-command delay tracking
  - AEM state
  - submit tracing callbacks
- `struct libnvme_mi_transport`, the internal transport vtable:
  - `submit`
  - `close`
  - endpoint description
  - timeout check
  - AEM file descriptor/read/purge operations
- MI endpoint helpers:
  - `libnvme_mi_init_ep()`
  - `libnvme_mi_ep_probe()`
  - `libnvme_mi_crc32_update()`
- MCTP socket mock operations for tests through `struct __mi_mctp_socket_ops` and `__libnvme_mi_mctp_set_ops()`.
- MI quirk flags:
  - `LIBNVME_QUIRK_MIN_INTER_COMMAND_TIME`
  - `LIBNVME_QUIRK_CSI_1_NOT_SUPPORTED`

Outside `CONFIG_MI`, it still declares transport-handle bridge functions:

- `__libnvme_transport_handle_open_mi()`
- `__libnvme_transport_handle_init_mi()`
- `__libnvme_transport_handle_close_mi()`

## Dependencies

- Conditional on `CONFIG_MI` for most definitions.
- Includes polling, socket, list, and public `nvme/mi.h` APIs.
- Uses CCAN intrusive lists.

## Research Notes

This header forms the internal boundary between generic libnvme transport handles and MI transports. The MCTP socket ops are intentionally private and test-oriented, allowing tests to replace socket operations without exposing the hook in the shared library ABI.

## Filesystem/Storage Relevance

MI is management-plane rather than data-plane. It supports storage inventory, health, and event processing for NVMe devices that may expose block namespaces.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private-mi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private.h

## Role

Central internal libnvme header. It defines Linux ioctl command shims, fabrics configuration, controller creation parameters, transport-handle state, topology object internals, stats state, global context state, private helpers, logging, and internal function prototypes.

## Key Content

- Declares sysfs path accessors:
  - `libnvme_subsys_sysfs_dir()`
  - `libnvme_ctrl_sysfs_dir()`
  - `libnvme_ns_sysfs_dir()`
  - `libnvme_slots_sysfs_dir()`
  - `libnvme_uuid_ibm_filename()`
  - `libnvme_dmi_entries_dir()`
- Defines Linux passthrough ioctl command layouts:
  - `struct linux_passthru_cmd32`
  - `struct linux_passthru_cmd64`
- Defines ioctl constants for reset, rescan, admin/io passthrough, and io_uring commands.
- Defines fabrics tuning:
  - `struct libnvme_fabrics_config`
  - `struct libnvme_ctrl_params`
  - `libnvme_fabrics_config_copy()`
- Defines transport handle state:
  - `enum libnvme_transport_handle_type`
  - `enum ioctl_state`
  - `enum libnvme_io_uring_state`
  - `struct libnvme_transport_handle`
- Defines topology and stats internals:
  - `struct libnvme_stat`
  - `struct libnvme_path`
  - `struct libnvme_ns_head`
  - `struct libnvme_ns`
  - `struct libnvme_ctrl`
  - `struct libnvme_subsystem`
  - `struct libnvme_host`
  - `struct libnvme_global_ctx`
- Defines fabrics option presence flags in `struct libnvme_fabric_options`.
- Declares JSON config/tree functions and core open/create/lookup functions.
- Declares fabrics and hostname/address helpers:
  - `traddr_is_hostname()`
  - `hostname2traddr()`
  - `libnvmf_default_config()`
  - `libnvmf_read_sysfs_fabrics_attrs()`
- Declares logging with `__libnvme_msg()` and `libnvme_msg()`.
- Provides small utilities:
  - `xstrdup()`
  - `streq0()`
  - `streqcase0()`
  - `round_up()`
- Declares key import, network address matching, key-value parsing, namespace transport handle management, MI admin passthrough, and io_uring open/close helpers.

## Dependencies

- Includes system stat/string headers, conditional `ifaddrs.h`, CCAN lists, internal/public NVMe type headers, and `nvme/tree.h`.
- Exposes conditional fields for `CONFIG_LIBURING`, `CONFIG_MI`, and `CONFIG_FABRICS`.
- Uses code-generation annotations for accessors and Python binding aliases.

## Research Notes

This file is the internal schema for libnvme's object graph. The public tree API is backed by these structs, but many fields are guarded by generated accessors or custom read/write annotations. The double-buffered stats in namespaces and paths are explicitly documented: `stat[curr_idx]` is current, `stat[!curr_idx]` is previous, and `diffstat` decides raw versus delta reporting.

## Filesystem/Storage Relevance

The file models how NVMe controllers, namespaces, paths, and hosts are represented in user space. It bridges sysfs topology, ioctl passthrough, io_uring passthrough, and fabrics configuration for storage tooling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/private.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/sysfs.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/sysfs.c

## Role

Provides centralized sysfs path resolution for libnvme.

## Key Content

- Defines default paths:
  - `/proc/device-tree/ibm,partition-uuid`
  - `/sys/block`
  - `/sys/bus/pci/slots`
  - `/sys/class/nvme-subsystem`
  - `/sys/class/nvme`
  - `/sys/firmware/dmi/entries`
- Implements `make_sysfs_dir()`, which prepends `LIBNVME_SYSFS_PATH` when the environment variable is set.
- Exposes cached path accessors:
  - `libnvme_subsys_sysfs_dir()`
  - `libnvme_ctrl_sysfs_dir()`
  - `libnvme_ns_sysfs_dir()`
  - `libnvme_slots_sysfs_dir()`
  - `libnvme_uuid_ibm_filename()`
  - `libnvme_dmi_entries_dir()`

## Dependencies

- Includes standard I/O and allocation headers plus internal `private.h`.

## Research Notes

Each accessor stores the computed path in a function-local static pointer. If `LIBNVME_SYSFS_PATH` is set, `asprintf()` allocates the prefixed string and the static pointer retains it for process lifetime. This is useful for tests, containers, or alternate sysfs roots.

## Filesystem/Storage Relevance

This file controls where libnvme looks for kernel block and NVMe topology information. The override mechanism is important for testing sysfs-backed storage discovery without requiring real hardware.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree-fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree-fabrics.c

## Role

Implements fabrics-specific topology matching and sysfs attribute harvesting for libnvme controller objects.

## Key Content

- Implements TCP controller matching when kernels do not expose `src_addr`:
  - `_tcp_ctrl_match_host_traddr_no_src_addr()`
  - `_tcp_ctrl_match_host_iface_no_src_addr()`
  - `_tcp_opt_params_match_no_src_addr()`
- Implements TCP controller matching when `src_addr` is available:
  - `_tcp_opt_params_match()`
  - `_tcp_match_ctrl()`
- Implements generic non-TCP matching:
  - `_libnvmf_tree_ctrl_match()`
- Initializes candidate matching state:
  - `libnvmf_candidate_init()`
  - `_libnvmf_candidate_init()`
- Reads fabrics security attributes from sysfs:
  - `libnvmf_read_sysfs_dhchap()`
  - `libnvmf_read_sysfs_tls()`
  - `libnvmf_read_sysfs_tls_mode()`
  - `libnvmf_read_sysfs_fabrics_attrs()`
- Public/internal lookup helpers:
  - `libnvme_ctrl_find()`
  - `libnvmf_ctrl_match_config()`
  - `libnvmf_ctrl_find()`

## Behavior

- TCP matching requires transport, `trsvcid`, destination `traddr`, discovery-controller state where relevant, and subsystem NQN where relevant.
- `host_traddr` and `host_iface` are optional TCP inputs. If a caller specifies either, the code tries to verify them.
- On kernels with `src_addr` in the controller `address` sysfs attribute, matching can infer source address and interface more accurately.
- On older kernels without `src_addr`, matching is intentionally optimistic when not enough data exists.
- Discovery controller matching handles the well-known discovery NQN specially: a controller connected with the well-known NQN may later expose a unique NQN, so the candidate records `well_known_nqn` and ignores direct NQN comparison.
- TLS sysfs values are parsed from hex string IDs into `cfg.tls_key_id` and `cfg.tls_configured_key_id`.

## Dependencies

- Includes networking, libnvme public headers, cleanup helpers, `private.h`, and `private-fabrics.h`.
- Uses helpers declared in `private.h`, including `streq0()`, `streqcase0()`, `libnvme_ipaddrs_eq()`, `libnvme_iface_matching_addr()`, and `libnvme_iface_primary_addr_matches()`.

## Research Notes

The core purpose is avoiding duplicate controller objects/connections while accounting for differences in kernel sysfs reporting across versions. The optimistic fallback on older kernels is explicitly documented as not perfectly accurate.

## Filesystem/Storage Relevance

Controller matching influences whether NVMe-oF paths/controllers are reused or duplicated in user-space topology. This affects how remote block devices are discovered, managed, and represented to higher-level storage tooling.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.c

## Role

Implements libnvme's sysfs-backed topology tree and many public tree APIs. It discovers hosts, subsystems, controllers, namespaces, namespace paths, sysfs attributes, transport handles, stats, basic namespace I/O helpers, configuration loading/dumping, and object lifecycle.

## Key Content

### Topology Scanning

- `libnvme_scan_topology()` scans controllers first, then subsystems, then applies an optional filter.
- Filtering helpers can remove subsystems, controllers, and namespaces after the tree is fully populated.
- `libnvme_refresh_topology()` frees current hosts and rescans.
- `libnvme_scan_ctrl()` discovers a controller from `/sys/class/nvme/<name>`.
- `libnvme_scan_namespace()` scans a namespace from the block sysfs path.
- `libnvme_rescan_ctrl()` refreshes namespaces and paths for an existing controller.

### Host and Subsystem Management

- `libnvme_host_get_ids()` resolves host NQN and host ID from, in order:
  - command-line arguments
  - first JSON-configured host
  - `/etc/nvme/hostid` and `/etc/nvme/hostnqn`
  - UUID embedded in host NQN
  - generated host ID/NQN fallback
- `libnvme_get_host()` resolves or creates a host object.
- `libnvme_lookup_host()` and `libnvme_lookup_subsystem()` find or allocate objects.
- `libnvme_init_subsystem()` reads subsystem attributes such as model, serial, firmware, `subsystype`, and `iopolicy`.
- Subsystem scan logic validates NQN consistency and creates a detached subsystem under the default host if needed.

### Controller Management

- `libnvme_ctrl_alloc()` parses controller transport/address data from sysfs and reuses existing controller objects through fabrics-aware matching.
- `libnvme_reconfigure_ctrl()` refreshes controller attributes, including firmware, model, state, queue count, serial, controller type, controller ID, discovery-controller type, physical slot, and fabrics security attributes.
- `libnvme_init_ctrl()` initializes a newly created controller instance from a kernel instance number.
- `libnvme_create_ctrl()` creates an in-memory controller from requested controller parameters.
- `libnvme_lookup_ctrl()` searches an existing subsystem for a matching controller or creates one.
- `nvme_deconfigure_ctrl()`, `libnvme_unlink_ctrl()`, and `libnvme_free_ctrl()` manage controller cleanup.

### Namespace and Path Management

- `libnvme_ns_open()` allocates a namespace and namespace head, detects modern multipath sysfs support, initializes namespace data, and sets generic names.
- `libnvme_ns_init()` reads namespace sysfs attributes:
  - `nsid`
  - `size`
  - logical block size
  - `eui`
  - `nguid`
  - `uuid`
  - optionally `csi`, `nuse`, and `metadata_bytes`
- If modern namespace attributes are unavailable, `libnvme_ns_init()` falls back to Identify Namespace passthrough.
- `libnvme_ctrl_scan_namespace()` links controller namespaces.
- `libnvme_subsystem_scan_namespace()` links subsystem namespaces.
- `libnvme_subsystem_set_ns_path()` associates namespace heads with path objects using modern multipath sysfs links where available, otherwise falls back to name parsing.
- `libnvme_ctrl_scan_path()` creates path objects and reads ANA state, NUMA nodes, ANA group ID, and queue depth.
- `libnvme_subsystem_lookup_namespace()` finds a namespace by NSID.

### Stats

- Path and namespace stats are double-buffered.
- `libnvme_update_stat()` parses Linux block `stat` format into read/write/discard/flush groups plus inflight and tick counters.
- Public getters return either raw counters or deltas depending on `diffstat`.
- Stats cover:
  - inflight I/O
  - I/O ticks
  - read/write ticks
  - read/write I/O counts
  - read/write sectors
  - sample interval

### Transport Handles and I/O Helpers

- Controllers and namespaces lazily open transport handles:
  - `libnvme_ctrl_get_transport_handle()`
  - `libnvme_ns_get_transport_handle()`
- Release helpers close cached handles.
- Namespace helpers issue common commands:
  - Identify Namespace
  - Identify Namespace Descriptors
  - Verify
  - Write Uncorrectable
  - Write Zeroes
  - Write
  - Read
  - Compare
  - Flush
- `libnvme_bytes_to_lba()` validates alignment and translates byte offset/count to starting LBA and zero-based block count.

### Config and Context

- `libnvme_read_config()`, `libnvme_dump_config()`, and `libnvme_dump_tree()` bridge to JSON config/tree functions.
- Application scoping is stored in the global context and can filter subsystem lookup.
- Object-freeing functions recursively release controllers, namespaces, paths, subsystems, hosts, and transport handles.

## Dependencies

- Uses sysfs scanning helpers from elsewhere in libnvme.
- Uses CCAN lists for intrusive object graph links.
- Uses cleanup macros for scoped cleanup.
- Uses public passthrough initializer helpers such as `nvme_init_identify_ns()`, `nvme_init_read()`, and `nvme_init_flush()`.
- Depends on private sysfs path helpers from `sysfs.c` and fabrics helpers from `tree-fabrics.c`.

## Research Notes

This file is the primary implementation of libnvme's view of kernel NVMe topology. It handles kernel-version drift explicitly, including older kernels lacking some sysfs namespace attributes and newer kernels exposing multipath namespace-head paths. It also supports `create_only` mode, where namespace/path scanning is skipped.

Memory ownership is manual but consistently handled through cleanup labels and recursive free helpers. The most error-prone areas are sysfs parsing, controller reuse matching, namespace/path linking by parsed names, and fallback Identify Namespace calls during namespace initialization.

## Filesystem/Storage Relevance

This is directly relevant to block-storage discovery. It maps kernel NVMe sysfs objects into user-space objects used by tools to inspect, configure, and operate NVMe controllers and namespaces. Namespace I/O helpers expose block-level operations that filesystems and storage diagnostics rely on indirectly.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/tree.c -->