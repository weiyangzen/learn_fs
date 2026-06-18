# Group Research: group_604_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__f78b9b83e606

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netstack.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netstack.h

## Purpose

`netstack.h` defines the illumos per-network-stack framework used by IP-adjacent kernel modules to maintain separate module state per shared or exclusive-IP zone. It is a public kernel coordination header for netstack identifiers, module registration, per-module lifecycle callbacks, kstat scoping, reference management, and stack iteration.

## Main Interfaces

The file defines `netstackid_t`, `GLOBAL_NETSTACKID`, and the ordered `NS_*` module slots from `NS_DLS` through `NS_ILB`. The ordering is explicitly meaningful: create callbacks run in ascending order and destruction runs in descending order.

Under `_KERNEL`, `nm_state_t` tracks per-module callback state with a flags word and condition variable. User-level consumers get a dummy `uint_t` type for build compatibility. The `NSS_*` flags distinguish needed, in-progress, and completed create/shutdown/destroy transitions.

`struct netstack` contains a typed union over module private pointers, a parallel `netstack_modules[NS_MAX]` array, per-module state, locks, linked-list pointer, stack id, zone usage count, hold/release reference count, lifecycle flags, and a kernel condition variable. Macros such as `netstack_ip`, `netstack_tcp`, and `netstack_ilb` provide typed field names for each slot.

`struct netstack_registry` stores callback function pointers for a module: create, shutdown, and destroy, plus registration flags.

Exported operations include initialization, hold/release, active holds, lookup by credentials/stack id/zone id, zone/stack id conversion, current-stack lookup, module registration/unregistration, netstack-scoped kstat create/delete, and iterator-style walking via `netstack_next_init()`, `netstack_next()`, and `netstack_next_fini()`.

## Runtime Use

This header does not implement control flow, but it defines the synchronization and lifecycle contract used by `netstack.c` and networking modules. Consumers register a module slot and callbacks, then store per-stack private state in the corresponding typed pointer inside `netstack_t`.

A caller that walks all netstacks must release every `netstack_t *` returned by `netstack_next()`. Most fields are protected by `netstack_lock`; `netstack_next` is protected by the global netstack lock.

## Dependencies

Includes `sys/kstat.h`, `sys/cred.h`, and `sys/mutex.h`. The typed module pointers are forward references to networking subsystem private stack structures such as `ip_stack`, `tcp_stack`, `udp_stack`, `sctp_stack`, `dls_stack`, and IPsec-related stack types.

## Risks and Invariants

The `NS_*` order is a hard lifecycle invariant. Adding or reordering slots can break dependency-sensitive create and destroy sequencing.

The union and accessor macros require `NS_MAX` and the typed field list to remain synchronized. A mismatch would corrupt module-private state indexing.

Reference ownership is explicit: lookups and iteration can return held stacks, and missing `netstack_rele()` calls leak references or block teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netstack.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nexusdefs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nexusdefs.h

## Purpose

`nexusdefs.h` defines shared DDI bus nexus operation enumerations. It is a small ABI-style header used by nexus and child drivers to classify control operations, bus configuration requests, and power-management notifications.

## Main Interfaces

`ddi_ctl_enum_t` enumerates bus nexus control operations including DMA mapping setup, child init/uninit, device and interrupt reporting, register sizing, affinity, I/O minimum, page/block conversions, power, attach/detach, quiesce/unquiesce, peek, and poke. Several obsolete operation numbers are preserved as `DDI_CTLOPS_RESERVED*` entries to maintain numeric compatibility.

`DDI_CTLOPS_REMOVECHILD` aliases `DDI_CTLOPS_UNINITCHILD` for old source compatibility.

`ddi_bus_config_op_t` defines bus enumeration/configuration/unconfiguration operations: enumerate, one/all/AP/driver config, one/driver/all/AP unconfig, and OBP argument-based config.

`pm_bus_power_op_t` defines bus power notifications and operations such as child power-change, nexus power-up, pre/post notification, has-changed, and no-involvement.

## Runtime Use

There is no executable logic. These enum values are consumed by bus framework callbacks and driver switch implementations to dispatch operation-specific behavior.

## Dependencies

The header is self-contained apart from C++ linkage guards.

## Risks and Invariants

The enum order is part of the interface. The reserved obsolete slots must not be collapsed or renumbered because existing compiled code and source assumptions may depend on historical numeric values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nexusdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/note.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/note.h

## Purpose

`note.h` provides the low-level `_NOTE()` annotation macro used throughout exported and kernel headers to embed source annotations for external tools without polluting user namespace with the preferred public `NOTE` macro.

## Main Interfaces

If `_NOTE` is not already defined, the header defines `_NOTE(s)` as an empty macro. Tooling can interpose a different `sys/note.h` implementation that expands annotations for static analysis or documentation.

## Runtime Use

There is no runtime behavior. In normal builds, annotations compile away completely.

## Dependencies

The file is self-contained and includes only C++ linkage guards.

## Risks and Invariants

Exported headers should use `_NOTE` rather than `NOTE` to avoid stealing names from consumers. Tool interposition relies on `_NOTE` being consistently used and normally inert.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/note.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/null.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/null.h

## Purpose

`null.h` centralizes the illumos definition of `NULL` across C, pre-C++11 C++, C++11 and later, and LP64/ILP32 modes.

## Main Interfaces

The header includes `sys/feature_tests.h` and only defines `NULL` if it is not already defined.

For C, `NULL` is `((void *)0)` to satisfy POSIX.1-2008. For C++11 and later, it is `nullptr`. For older C++, it is an integral zero constant: `0L` on LP64 and `0` otherwise.

## Runtime Use

There is no runtime behavior. The value affects compile-time overload resolution and pointer/null conversions.

## Dependencies

Depends on feature-test and compiler macros: `__cplusplus` and `_LP64`.

## Risks and Invariants

The split definitions are intentional. Changing the C++ form can affect overload resolution; changing the C form can break POSIX expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme.h

## Purpose

`nvme.h` is the central shared ABI header between `nvme(4D)` and libnvme/userland. It defines NVMe ioctl numbers, ioctl payload structures, detailed driver-specific error reporting, identify/log/feature data structures, completion status constants, namespace state reporting, and ILP32 compatibility structures.

## Main Interfaces

The ioctl namespace is rooted at `NVME_IOC` and includes controller info, identify, get log page, get feature, format, blkdev attach/detach, firmware download/commit, vendor passthrough, namespace info, locks, controller attach/detach, namespace create/delete, and helpers `IS_NVME_IOC()` and `NVME_IOC_CMD()`.

`nvme_ioctl_errno_t` is a large driver error taxonomy. It separates kernel ioctl transport errors from semantic NVMe validation errors and controller completion errors. It covers controller death/removal, namespace targeting, lock requirements, log page validation, DMA/PRP/user-buffer faults, identify validation, vendor command validation, blkdev state, format and firmware failures, feature validation, lock sequencing, namespace management, and namespace create errors.

Every ioctl payload starts with `nvme_ioctl_common_t`, which carries `nioc_nsid`, `nioc_drv_err`, and optional controller SCT/SC status. Major ioctl structures include identify, get feature, get log page, passthrough, firmware load/commit, format, lock/unlock, namespace create, controller info, and namespace info.

The header defines NVMe version helpers, namespace constants, packed 128-bit integer representation, identify controller and namespace structures, identify lists/descriptors, primary-controller capabilities, completion status fields, log page IDs, log page structures, feature IDs and feature payload encodings, firmware constants, completion status codes, namespace state enum, and command set identifiers.

The identify controller and namespace structures are full packed mirrors of NVMe specification data, including fields through recent NVMe 2.x/2.3 additions such as FDP, device personalities, power measurement, reachability, dispersed namespaces, and power limit support.

## Runtime Use

The header itself contains no functions. Runtime behavior is defined by the ABI contracts:

1. Userland fills an ioctl structure with a common header and command-specific fields.
2. `nvme(4D)` validates namespace/minor targeting, controller capability, version support, field ranges, lock state, buffer sizes, and command support.
3. On success, data is copied to/from the supplied user pointer or returned in command result fields.
4. On failure after initial ioctl setup, `nioc_drv_err` identifies the precise semantic error, avoiding overloaded `errno` meanings.

The packed NVMe data structures are also used to interpret controller identify buffers and log-page payloads returned by hardware.

## Dependencies

Kernel builds use `sys/types32.h` for 32-bit ioctl compatibility. Userland builds use `sys/uuid.h` and `<stdint.h>`. The header also depends on `sys/types.h`, `sys/debug.h`, and `sys/stddef.h`.

Related users include the NVMe driver, libnvme discovery/control APIs, and the vendor-specific NVMe headers in `sys/nvme/`.

## Risks and Invariants

This is an ABI header. Structure layout, packing, enum values, ioctl numbers, and field sizes must remain stable or intentionally versioned.

The 32-bit ioctl structures under `_KERNEL && _SYSCALL32` must match ILP32 layout exactly; pointer-size or packing mistakes break 32-bit userland.

Packed bitfields mirror hardware/spec layout and can be sensitive to compiler, endian, and specification changes. Existing `CTASSERT()` checks protect selected structure sizes and offsets.

There is a duplicate `#define NVME_FEAT_IO_CMD_SET 0x19`; it is harmless because both definitions are identical, but it is a maintenance smell.

The file intentionally distinguishes range, unsupported, and unusable errors. New ioctl validation should preserve that taxonomy so libnvme can present precise diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/discovery.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/discovery.h

## Purpose

`nvme/discovery.h` defines common enums used by libnvme discovery APIs to describe NVMe log pages and features: their kind, scope, discovery evidence source, required request fields, support state, and command-set applicability.

## Main Interfaces

For log pages, it defines `nvme_log_disc_kind_t`, `nvme_log_disc_scope_t`, `nvme_log_disc_source_t`, and `nvme_log_disc_fields_t`. These classify logs as mandatory/optional/vendor-specific, scoped to controller/NVM subsystem/namespace, sourced from spec/identify/database/command probing, and requiring LSP/LSI/RAE/NSID.

For features, it defines controller/namespace scope, get-feature required fields, set-feature required fields, feature output locations, feature flags for broadcast namespace support, feature kind, command-set applicability, and implementation status.

`nvme_feat_impl_t` allows discovery to report unknown, unsupported, or supported, reflecting the fact that pre-NVMe-2.x devices often have no standard feature-support enumeration.

## Runtime Use

No logic is implemented here. Discovery code populates these enum values after combining specification rules, identify-controller bits, internal vendor databases, and command-based probing.

## Dependencies

The header is self-contained with C++ guards.

## Risks and Invariants

The flags are bitmasks; consumers may combine values. New discovery flags must not collide with existing bits.

The distinction between unknown and unsupported is important for pre-2.x devices where absence of evidence is not proof of absence.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/discovery.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia.h

## Purpose

`nvme/kioxia.h` is the Kioxia vendor aggregation header for uncommitted NVMe vendor-specific interfaces.

## Main Interfaces

It includes `sys/nvme/kioxia_cd8.h` and defines the Kioxia PCI vendor ID:

- `KIOXIA_PCI_VID` = `0x1e0f`

## Runtime Use

There is no runtime logic. Consumers include this header to get common Kioxia vendor IDs and the currently known Kioxia device-family definitions.

## Dependencies

Depends on `kioxia_cd8.h`.

## Risks and Invariants

The header explicitly states that the interface is not committed. Consumers should not treat these definitions as stable public ABI beyond matching the illumos/libnvme version they were built against.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia_cd8.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia_cd8.h

## Purpose

`nvme/kioxia_cd8.h` defines uncommitted vendor-specific NVMe identifiers and log layouts for Kioxia CD8 and CD8P devices.

## Main Interfaces

Device IDs:

- `KIOXIA_CD8_DID` = `0x1f`
- `KIOXIA_CD8P_DID` = `0x2b`

`kioxia_cd8_vul_t` maps supported vendor log IDs, mostly to OCP Datacenter SSD logs, plus `KIOXIA_CD8_LOG_EXTSMART` at `0xca`.

The packed `kioxia_extsmart_ent_t` is a 12-byte SMART entry with ID, normalized value, raw six-byte value, and reserved bytes. `kioxia_smart_type_t` defines known entry IDs such as program fail, erase fail, wear level, E2E error, CRC error, NAND write, and host write.

`kioxia_vul_cd8_smart_t` maps the 512-byte CD8 extended SMART log layout, including fixed positions for Kioxia-specific entries and later standard SMART-like entries. `CTASSERT()` checks enforce 12-byte entries and 512-byte log size outside smatch.

## Runtime Use

Consumers issue the relevant vendor log-page request and cast/parse the returned 512-byte buffer according to the packed structures. Entry IDs should be validated when interpreting fields.

## Dependencies

Includes `sys/debug.h` and `sys/nvme/ocp.h`.

## Risks and Invariants

All structures must remain packed and size-checked against vendor manuals. Misalignment or wrong reserved-region sizes would misinterpret device telemetry.

The file is guarded for smatch because the current checker cannot handle packed structure size assertions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/kioxia_cd8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron.h

## Purpose

`nvme/micron.h` is the Micron vendor aggregation header and shared Micron vendor-log definition point for uncommitted NVMe vendor-specific interfaces.

## Main Interfaces

It includes Micron family headers for 7300, 74x0, x500, and 9550 devices, and defines:

- `MICRON_PCI_VID` = `0x1344`

The packed `micron_vul_ext_smart_t` models Micron's common 256-byte extended SMART log used across several generations, with newer fields marked as 7400+ specific. It includes grown bad block count, max erase count, power-on count, write-protect reason, capacity, erase count, use rate, erase fail, UECC, program fail, read/write bytes, translation size, bad-block statistics, and user erase min/avg/max.

`micron_vul_wp_reason_t` defines write-protect reason bits such as DRAM double-bit error, low spare blocks, capacitor failure, NVRAM checksum, DRAM range, and over-temperature.

## Runtime Use

Micron-specific discovery and telemetry code uses device-family IDs to select the proper log ID and then parses the returned extended SMART payload with this common structure where applicable.

## Dependencies

Includes Micron family headers. Uses `CTASSERT()` via included dependencies or build context, and packed layout pragmas.

## Risks and Invariants

The log layout differs by generation. Fields marked 7400+ must be treated as reserved or unsupported on older devices.

The packed structure must remain exactly `0x100` bytes. Misinterpreting the write-protect bitmask could lead to wrong device health diagnosis.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_7300.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_7300.h

## Purpose

`nvme/micron_7300.h` defines uncommitted vendor-specific identifiers and SMART log structures for Micron 7300 Pro/Max devices.

## Main Interfaces

Device IDs:

- `MICRON_7300_PRO_DID` = `0x51a2`
- `MICRON_7300_MAX_DID` = `0x51a3`

`micron_7300_vul_t` defines log `0xca` for an older SMART log and log `0xd0` for the preferred `micron_vul_ext_smart_t`.

The packed `micron_vul_smart_ent_t` is a 12-byte entry with type, reserved bytes, and seven data bytes. `micron_vul_smart_t` contains six fixed entries: writes, reads, throttle, life/temp, power, and power-on temperature. A `CTASSERT()` verifies total size `0x48`.

## Runtime Use

Telemetry consumers may read the legacy `0xca` SMART log or prefer the common extended SMART log at `0xd0` when available.

## Dependencies

Includes `sys/debug.h` and `sys/stdint.h`.

## Risks and Invariants

The legacy entry payload interpretation varies by type and is not self-describing beyond fixed position and type. Consumers should validate types and prefer the extended SMART log where possible.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_7300.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_74x0.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_74x0.h

## Purpose

`nvme/micron_74x0.h` defines Micron 7400/7450 Pro/Max device IDs and the vendor log ID for the extended SMART log.

## Main Interfaces

Device IDs:

- `MICRON_7400_PRO_DID` = `0x51c0`
- `MICRON_7400_MAX_DID` = `0x51c1`
- `MICRON_7450_PRO_DID` = `0x51c3`
- `MICRON_7450_MAX_DID` = `0x51c4`

`micron_74x0_vul_t` defines `MICRON_74x0_LOG_EXT_SMART` = `0xe1`.

## Runtime Use

Consumers match device IDs and request log page `0xe1`, interpreted using the common Micron extended SMART structure from `micron.h`.

## Dependencies

Self-contained with C++ guards; normally included through `micron.h`.

## Risks and Invariants

The file relies on the common Micron header for the actual payload structure. Device ID matching must distinguish Pro/Max variants but the log ID is shared.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_74x0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_9550.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_9550.h

## Purpose

`nvme/micron_9550.h` defines uncommitted vendor-specific identifiers and OCP log mappings for Micron 9550 series NVMe devices.

## Main Interfaces

Device IDs:

- `MICRON_9550_PRO_DID` = `0x51bb`
- `MICRON_9550_MAX_DID` = `0x51bd`

`micron_9500_vul_t` maps Micron 9550 log aliases to OCP Datacenter SSD logs: SMART, error recovery, firmware activation, latency, device capability, unsupported requirements, and telemetry.

## Runtime Use

Consumers identify 9550 devices by PCI ID and use OCP log structures from `ocp.h` for the listed telemetry pages.

## Dependencies

Uses OCP log constants, but does not directly include `ocp.h`; it is included indirectly through the aggregation context in `micron.h` only if already available. Direct inclusion may require include-order care.

## Risks and Invariants

The enum type name `micron_9500_vul_t` differs from the file/device family name `9550`, likely a naming inconsistency. Consumers should use the constants, not infer family from the typedef name.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_9550.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_x500.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_x500.h

## Purpose

`nvme/micron_x500.h` defines uncommitted vendor-specific identifiers and OCP log mappings for Micron 6500 and 7500 series devices.

## Main Interfaces

Device IDs:

- `MICRON_6500_ION_DID` = `0x51b9`
- `MICRON_7500_PRO_DID` = `0x51b7`
- `MICRON_7500_MAX_DID` = `0x51b8`

`micron_x500_vul_t` maps OCP SMART, error recovery, firmware activation, latency, device capability, and unsupported-requirements logs.

## Runtime Use

Device matching code uses the PCI device ID to select these log-page aliases, then parses payloads with OCP structures.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The interface is uncommitted and vendor-specific. The x500 family name spans multiple product generations, so future devices may need additional payload distinctions even when log IDs are shared.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/micron_x500.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/ocp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/ocp.h

## Purpose

`nvme/ocp.h` defines uncommitted vendor-specific NVMe interfaces for the OCP Datacenter NVMe SSD specifications, covering versions 2.0 and 2.5 and the earlier Cloud SSD lineage.

## Main Interfaces

`ocp_vul_t` defines OCP log IDs for SMART, error recovery, firmware activation, latency monitor, device capabilities, unsupported requirements, TCG configuration, and telemetry strings. `ocp_vuf_t` defines OCP feature IDs for error injection, clearing firmware activation history, EOL/PLP behavior, PCIe correctable error clear, IEEE1667, latency monitor, PLP health, power state, telemetry profile, and async events.

All payload structures are packed and little-endian. Major log structures include:

- `ocp_vul_smart_t`: 512-byte SMART/health log with physical media reads/writes, NAND block health, recovery/error counters, erase counts, thermal throttling, DSSD version, PCIe errors, incomplete shutdowns, free percentage, capacitor health, unaligned I/O, security version, namespace utilization, PLP events, endurance estimate, retrains, power-state changes, min firmware rollback, version, and GUID.
- `ocp_vul_errrec_t`: 512-byte error recovery log with reset timing, panic reset actions, device recovery actions, panic IDs, vendor recovery command fields, secondary recovery, old panic IDs, version, and GUID.
- `ocp_vul_fwact_t`: 4096-byte firmware activation history log with 20 fixed 64-byte entries.
- `ocp_vul_lat_t`: 512-byte latency monitor log with active/static bucket counters, latency timestamps, measured latency, debug trigger metadata, version, and GUID.
- `ocp_vul_devcap_t`: 4096-byte capability log including power-state descriptors and capability bitfields.
- `ocp_vul_unsup_req_t`: 4096-byte unsupported requirements log with 253 fixed 16-byte requirement strings.
- `ocp_vul_telstr_t` and table-entry structures for OCP 2.5 telemetry string logs.

Associated enums define reset-action bits, recovery-action bits, device capability bits, latency monitor feature/configuration bits, and capability flags for out-of-band, write-zeroes, dataset management, write-uncorrectable, and fused operations.

## Runtime Use

Vendor-specific headers alias device-family log IDs to these OCP constants. Consumers request the log page, verify version/GUID where appropriate, and parse the packed payload. Several logs carry variable-length trailing data or string tables, so consumers must use header offsets and lengths rather than assuming null-terminated strings.

## Dependencies

Includes `sys/isa_defs.h`, `sys/debug.h`, `sys/stdint.h`, and `sys/stddef.h`. Uses endian bitfield guards and extensive `CTASSERT()` checks.

## Risks and Invariants

All structures are hardware/spec ABI mirrors. Packing, little-endian interpretation, structure sizes, offsets, version values, and GUIDs are critical.

String-like fields are often byte arrays, fixed-width, padded, or counted; they must not be treated as trusted C strings.

The unsupported-requirements strings are explicitly untrusted byte arrays and may not be null-terminated.

A duplicate `CTASSERT(offsetof(ocp_vul_errrec_t, oer_npanic) == 31)` appears twice; it is harmless but redundant.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/ocp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/phison.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/phison.h

## Purpose

`nvme/phison.h` defines uncommitted Phison vendor-specific NVMe IDs and OCP log aliases for known Phison devices.

## Main Interfaces

Vendor/device IDs:

- `PHISON_PCI_VID` = `0x1987`
- `PHISON_X200_DID` = `0x5302`

`phison_x200_vul_t` maps X200 log aliases to OCP SMART, error recovery, firmware activation, latency, device capabilities, and unsupported requirements.

## Runtime Use

Device-specific discovery code matches Phison X200 devices and treats the listed vendor logs as OCP Datacenter SSD payloads.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The header declares an uncommitted interface. Correctness depends on the X200 conforming to OCP log layouts for these IDs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/phison.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/samsung.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/samsung.h

## Purpose

`nvme/samsung.h` defines uncommitted Samsung vendor-specific NVMe IDs and OCP log aliases for Samsung PM9D3 devices.

## Main Interfaces

Vendor/device IDs:

- `SAMSUNG_PCI_VID` = `0x144d`
- `SAMSUNG_PM9D3_DID` = `0xa900`

`samsung_pm9d3_vul_t` maps PM9D3 logs to OCP SMART, error recovery, firmware activation, latency, device capabilities, unsupported requirements, TCG, and telemetry logs.

## Runtime Use

Discovery/telemetry code matches Samsung PM9D3 devices and parses the listed vendor logs with OCP structures.

## Dependencies

Includes `sys/nvme/ocp.h`.

## Risks and Invariants

The file comment incorrectly says it contains entries for known Phison devices, a copy/paste documentation error. The constants themselves are Samsung-specific.

OCP telemetry and TCG logs require OCP 2.5-aware parsing; older OCP assumptions are insufficient.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/samsung.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm.h

## Purpose

`nvme/solidigm.h` aggregates Solidigm and legacy Intel NVMe vendor definitions, and defines common packed payload structures shared across Solidigm device families.

## Main Interfaces

Vendor IDs:

- `INTEL_PCI_VID` = `0x8086`
- `SOLIDIGM_PCI_VID` = `0x25e`

The header includes P5xxx and PS10x0 family headers.

Common packed structures:

- `solidigm_smart_ent_t`: 12-byte device-specific SMART entry with type, normalized value, raw six-byte payload, and reserved bytes.
- `solidigm_smart_type_t`: entry type IDs for program/erase failures, wear level, E2E/CRC errors, timed media wear/read/timer values, in-flight read/write, thermal throttling, retry buffer overflow, PLL loss, NAND/host write, system life, NAND read, firmware download availability, read/write collision, and XOR stats.
- `solidigm_vul_smart_log_t`: up to one 512-byte log page of 12-byte entries.
- `solidigm_vul_temp_t`: 112-byte common temperature log with current, over-threshold, lifetime, composite high/low, warning max, minimum operating, and estimated offset fields.

`CTASSERT()` checks enforce structure sizes and range expectations.

## Runtime Use

Solidigm family-specific headers refer to these common structures for SMART and temperature logs. Consumers should parse SMART entries by entry type because order may vary or holes may exist.

## Dependencies

Includes `solidigm_p5xxx.h` and `solidigm_ps10x0.h`. Uses packed layout and `CTASSERT()`.

## Risks and Invariants

`SOLIDIGM_PCI_VID` is written as `0x25e`; consumers should treat it as the numeric value from the header, though conventional PCI vendor IDs are often displayed zero-padded.

The SMART log can contain entries in arbitrary order. Code that assumes array index equals semantic meaning may misread telemetry.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_p5xxx.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_p5xxx.h

## Purpose

`nvme/solidigm_p5xxx.h` defines uncommitted vendor-specific interfaces for Intel/Solidigm P5510, P5520, and P5620 NVMe devices.

## Main Interfaces

The family shares PCI device ID `SOLIDIGM_P5XXX_DID` = `0xb60`; subsystem IDs distinguish P5510 U.2, P5520 U.2/E1.S/E1.L, and P5620 U.2 variants.

`solidigm_p5xxx_vul_t` defines log IDs for the P5510 directory, P5x20 OCP SMART, read/write latency histograms, temperature, SMART, I/O queue state, marketing description, power, garbage collection, and latency outliers.

Packed payload structures include:

- `solidigm_vul_p5xxx_lat_t`: 4876-byte read/write latency histogram with 19 groups of 64 buckets plus average latency.
- `solidigm_vul_iosq_t` and `solidigm_vul_iocq_t`: I/O submission/completion queue snapshots.
- `solidigm_vul_p5xxx_ioq_t`: 1024-byte queue log for up to 32 IOSQs and IOCQs.
- `solidigm_vul_p5x2x_power_t`: two 32-bit power readings in microwatts.
- `solidigm_vul_gc_ent_t` and `solidigm_vul_p5xxx_gc_t`: garbage-collection event log.
- `soligm_vul_lat_ent_t` and `solidigm_vul_p5xxx_lat_outlier_t`: variable-length latency outlier log.

`SOLIDIGM_VUL_MAX_QUEUES`, `SOLIDIGM_VUC_MARK_NAME_LEN`, and `SOLIDIGM_VUC_MAX_GC` define parser bounds.

## Runtime Use

Consumers must disambiguate devices by subsystem ID, select the correct log bucket, and parse fixed or variable-length payloads according to the log ID. Latency logs require prior device configuration through vendor-specific feature control to contain useful data.

## Dependencies

Includes `sys/stdint.h`, `sys/debug.h`, `sys/stddef.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The shared device ID makes subsystem ID matching mandatory.

Latency histogram field names encode bucket ranges and widths; parser math should match the documented ranges rather than assume uniform buckets.

`soligm_vul_lat_ent_t` appears to miss the second `d` in `solidigm`, a typedef spelling inconsistency that consumers must use as written.

Variable-length outlier logs require bounds checks against returned buffer length and `lao_nents`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_p5xxx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_ps10x0.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_ps10x0.h

## Purpose

`nvme/solidigm_ps10x0.h` defines uncommitted vendor-specific identifiers and log aliases for Solidigm/Intel PS1010 and PS1030 devices.

## Main Interfaces

Device and subsystem IDs identify PS1010/PS1030 and U.2/E3 variants:

- `SOLIDIGM_PS10X0_DID` = `0x2B59`
- `SOLIDIGM_PS1010_U2_SDID`, `SOLIDIGM_PS1010_E3_SDID`
- `SOLIDIGM_PS1030_U2_SDID`, `SOLIDIGM_PS1030_E3_SDID`

`solidigm_ps10x0_vul_t` maps OCP logs plus Solidigm SMART log `0xca` and temperature log `0xd5`. The SMART log uses `solidigm_vul_smart_log_t`; the temperature log uses `solidigm_vul_temp_t`.

## Runtime Use

Consumers match device/subsystem IDs, request OCP or Solidigm-specific log pages, and parse SMART entries allowing holes.

## Dependencies

Uses OCP constants and common Solidigm structures, normally through inclusion from `solidigm.h`.

## Risks and Invariants

Direct inclusion without prior OCP/common Solidigm definitions may require include-order care. SMART log parsing must not assume all possible entries are present.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/solidigm_ps10x0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc.h

## Purpose

`nvme/wdc.h` aggregates WDC/Sandisk vendor-specific NVMe definitions and common WDC payload structures and vendor command constants.

## Main Interfaces

Includes WDC family headers for SN840, SN65x, and SN861. Defines:

- `WDC_PCI_VID` = `0x1b96`

Common packed structures:

- `wdc_vul_power_t`: variable-length power sample log, samples in milliwatts.
- `wdc_vul_temp_t`: variable-length temperature sample log, temperatures in Celsius with family-specific sample-index enums.
- `wdc_vsd_t`: variable-length device manageability entry with length, ID, and data; entries are 4-byte aligned.
- `wdc_cbs_t`: counted byte string with little-endian length and non-null-terminated data.
- `wdc_e6_header_t`: 8-byte diagnostic dump header for opcode `0xe6`.

Vendor command constants cover the E6 diagnostic dump command, destructive resize command `0xcc`, and assert clear/inject command `0xd8`.

## Runtime Use

Family-specific headers reuse the common power/temp/manageability structures. Diagnostic dump readers first fetch the E6 header to determine total byte size, then read dword ranges using command offset fields. Resize and assert commands use specific subcommand encodings in command dwords.

## Dependencies

Includes the WDC family headers. Uses packed layout and `CTASSERT()`.

## Risks and Invariants

The resize command is explicitly destructive. Tooling must gate it behind strong user confirmation and correct lock/state checks.

`wdc_cbs_t` is not a C string; code must obey `cbs_len` and account for 4-byte padding.

The E6 dump size is stored as a big-endian-style size field while commands use dword counts, so byte/dword conversion and endian handling are critical.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn65x.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn65x.h

## Purpose

`nvme/wdc_sn65x.h` defines uncommitted vendor-specific IDs, log IDs, temperature sample indexes, and SMART log layout for WDC SN650 and SN655 devices.

## Main Interfaces

Device IDs:

- `WDC_SN650_DID` = `0x2720`
- `WDC_SN655_DID` = `0x2722`

`wdc_sn65x_vul_t` defines OCP SMART, common power log `0xc5`, common temperature log `0xc6`, and unique SMART log `0xca`.

`wdc_sn65x_temp_sample_t` enumerates temperature sample positions including board sensors, inlet/outlet, NAND, front-end, flash modules, thermistor, averages, and `WDC_SN65X_TEMP_NSAMPLES`.

The packed `wdc_vul_sn65x_smart_ent_t` is a 12-byte customer-unique SMART entry. `wdc_vul_sn65x_smart_t` defines fixed entries for program/erase failures, wear, E2E, CRC, timed wear/read/timer, thermal throttling, retry overflow, PLL loss, NAND written, and host written. `wdc_sn65x_smart_ent_id_t` defines expected entry IDs.

## Runtime Use

Consumers request SN65x power/temp/SMART logs and use the family-specific sample and entry enums to interpret variable/common structures and fixed unique SMART entries.

## Dependencies

Includes `sys/debug.h`, `sys/stdint.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The SMART enum contains spelling inconsistencies such as `END_ID`, `ETOE`, and `THROTLE`; consumers must use the defined names or compare numeric values.

The unique SMART log comment says entry IDs should be validated. Failing to validate IDs can silently mislabel telemetry if firmware layout changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn65x.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn840.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn840.h

## Purpose

`nvme/wdc_sn840.h` defines uncommitted WDC SN840 vendor-specific IDs, log IDs, device manageability entry IDs, temperature sample indexes, and packed log structures.

## Main Interfaces

Device ID:

- `WDC_SN840_DID` = `0x2500`

`wdc_sn840_vul_t` defines log IDs for EOL, device manageability, PCIe SI, power, temperature, firmware activation, and CCDS info.

Packed payloads include:

- `wdc_vul_sn840_eol_t`: 118-byte EOL status log with read/write amplification, PLR, failure counts, vendor/customer/system status, and state fields.
- `wdc_vul_sn840_fw_act_ent_t`: 48-byte firmware activation entry.
- `wdc_vul_sn840_fw_act_hdr_t`: 16-byte firmware activation header with version, entry count, and entry length.
- `wdc_vul_sn840_ccds_info_t`: 36-byte CCDS information block.

`wdc_sn840_vsd_id_t` enumerates many device manageability entry IDs, including firmware versions, capacities, supported logs/features, form factor, namespace details, part/serial/product strings, thermal/assert/EOL status, and reset sequence metadata. `wdc_sn840_vsd_ns_id_t` defines namespace-scoped supported log/feature IDs. `wdc_sn840_temp_sample_t` defines temperature sample indexes.

## Runtime Use

Consumers parse SN840 log pages by log ID. Device manageability logs use common `wdc_vsd_t` and `wdc_cbs_t` structures from `wdc.h`, with each entry ID determining whether the payload is integer or counted byte string.

## Dependencies

Includes `sys/debug.h` and `sys/stdint.h`; `sys/debug.h` is included twice.

## Risks and Invariants

Several logs are variable-length or table-based. Consumers must use header entry counts/lengths and VSD lengths rather than fixed buffer assumptions.

`WDC_SN840_LOG_PCIE_SI` is known to exist but has unknown data format; tools should expose raw data or mark it unsupported rather than inventing a parser.

The temperature enum ends with `WDC_SN840_TEMP_NSMAPLES`, a spelling typo that is part of the header API.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn840.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn861.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn861.h

## Purpose

`nvme/wdc_sn861.h` defines uncommitted Sandisk/WDC SN861 vendor-specific IDs, OCP log aliases, and vendor command constants.

## Main Interfaces

Device IDs distinguish form factors:

- `WDC_SN861_DID_E1` = `0x2750`
- `WDC_SN861_DID_U2` = `0x2751`
- `WDC_SN861_DID_E3` = `0x2752`

`wdc_sn861_vul_t` maps OCP SMART, error recovery, firmware activation, latency, device capabilities, and unsupported requirements.

Vendor command constants use opcode `0xd2` for PCIe eye diagram retrieval and hardware revision retrieval. Eye retrieval uses `WDC_SN861_VUC_EYE_CDW12`, lane in `cdw13`, and a fixed upper-bound length `WDC_SN861_VUC_EYE_LEN`. Hardware revision uses `WDC_SN861_VUC_HWREV_CDW12`.

## Runtime Use

Consumers match SN861 variants by device ID, parse standard OCP logs, and use vendor passthrough for eye diagram or hardware revision commands.

## Dependencies

Includes `sys/debug.h`, `sys/stdint.h`, and `sys/nvme/ocp.h`.

## Risks and Invariants

The eye diagram command returns a large fixed upper-bound payload. Callers must validate buffer size, lane selection, and command timeout.

Both vendor commands share opcode `0xd2` and differ by `cdw12`; subcommand selection must be exact.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvme/wdc_sn861.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair.h

## Purpose

`nvpair.h` defines the public illumos name-value pair and name-value list API used across kernel and userland for typed property lists, packing/unpacking, lookup, mutation, and fail-fast convenience wrappers.

## Main Interfaces

`data_type_t` enumerates supported value types: booleans, bytes, signed/unsigned integer widths, strings, arrays, hrtime, nested nvlist, nvlist arrays, and userland-only double. Kernel builds omit `DATA_TYPE_DOUBLE`.

`nvpair_t` defines the packed pair header: size, name size, element count, and type, followed by name and aligned value data. `nvlist_t` defines list header fields: version, persistent flags, private implementation pointer, runtime flags, and padding.

Constants define version, native/XDR encoding, uniqueness flags, lookup flags, alignment helpers, and macros for pair/list field access.

The allocator framework consists of `nv_alloc_t`, `nv_alloc_ops_t`, fixed/nosleep/sleep allocators, and init/reset/fini functions.

The main API covers allocation/free, size, pack/unpack, dup, merge, custom allocator variants, add/remove operations for every supported type, lookup operations for every supported type, pair existence/emptiness checks, pair iteration, pair field accessors, and value extraction from `nvpair_t`.

The `fnvlist_*` and `fnvpair_*` family provides fail-fast convenience wrappers that return values directly or abort/panic on allocation/lookup failure depending on environment.

## Runtime Use

Callers allocate an `nvlist_t`, add typed name-value pairs, optionally pack it for transport/storage, unpack it later, and look up values by name and type. Kernel callers can choose sleep/nosleep allocation behavior; userland can use allocator variants or defaults.

## Dependencies

Includes `sys/types.h`, `sys/time.h`, `sys/errno.h`, and `sys/va_list.h`. Kernel non-boot builds include `sys/kmem.h`.

Implementation-private details live in `nvpair_impl.h`.

## Risks and Invariants

The on-wire/in-memory packed layout depends on alignment macros and type enum values. Changes can break native/XDR compatibility.

The `NVL_SIZE(nvl)` macro references `nvl_size`, which is not a member of the visible `nvlist_t`; it likely applies only to packed/internal layouts and should be used carefully.

String and array lookup APIs return pointers owned by the nvlist; callers must not free or outlive the list unless documented by implementation behavior.

Fail-fast `fnvlist_*` wrappers are convenient but inappropriate where recoverable allocation or missing-key errors must be surfaced.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair_impl.h

## Purpose

`nvpair_impl.h` exposes internal nvpair/nvlist implementation structures for information and debugging. It is not a stable public implementation contract.

## Main Interfaces

`i_nvp_t` wraps an `nvpair_t` with implementation linkage. Its union ensures 64-bit alignment and stores next, previous, and hash-bucket next pointers. Macros expose `nvi_next`, `nvi_prev`, and `nvi_hashtable_next`.

`nvpriv_t` stores the private state behind an unpacked nvlist: linked-list head, last pair, current walker pair, allocator, internal state flags, hash table pointer, bucket count, and entry count.

## Runtime Use

The nvpair implementation uses these structures to manage ordered iteration and faster lookup through a hash table. Debuggers and low-level implementation code can inspect them.

## Dependencies

Includes `sys/nvpair.h`.

## Risks and Invariants

The header explicitly says these structures may change. External code should not depend on their layout for ABI stability.

`i_nvp_t` embeds `nvpair_t` after link fields; any code converting between public and private pair pointers must use implementation-approved helpers or known layout carefully.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nvpair_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge.h

## Purpose

`nxge/nxge.h` is the primary private/public driver header for the Neptune/NIU `nxge` Ethernet driver. It defines diagnostic ioctl numbers, driver parameters, statistics, interrupt state, ring/group virtualization state, the main per-instance `nxge_t` state object, kstat layouts, and core prototypes.

## Main Interfaces

The `NXGE_IOC` command namespace defines diagnostic and maintenance ioctls for register reads/writes, ring descriptor inspection, resets, MII access, tracing, register dumps, TCAM access, error injection, RX classification, and RX hashing.

Driver constants define module info, STREAMS packet sizes/watermarks, timers, compatibility strings, and status values.

`nxge_param_index_t` enumerates all tunable or reportable driver parameters, including instance metadata, firmware/port mode, autonegotiation, advertised capabilities, pause settings, DMA channel counts and groups, RDC defaults, interrupt moderation, classification, TCAM/hash controls, debug flags, and dump controls.

`nxge_param_t` describes named dispatch parameters with get/set callbacks, type flags, min/max/current/old values, firmware-code name, and user-visible name. Parameter flags encode read/write/shared/private, subsystem category, initialization-only, property source, numeric base, visibility, and array metadata.

The file defines link-loopback modes, MAC state, DLPI address structures, multicast hash tables, filters, port statistics, aggregate statistics/kstat handles, interrupt state, logical-device/group vectors, Crossbow/hybrid-I/O group and ring handles, share handles, and the large `struct _nxge_t` per-device instance state.

`struct _nxge_t` aggregates devinfo, register handles, NPI handles, transceiver/MAC/IPP/TXC/classifier state, MAC framework handle, statistics, tunables, hardware-list pointer, platform/NIU type, DMA pools/rings/mailboxes, PHY/MII state, filters, timers, FMA state, port ring sizing, multi-MAC info, sun4v hypervisor state, link polling, magic value, LSO flag, LDOM/Hybrid I/O state, ring/group/share arrays, and NIU hardware type.

Kstat structures define named counters for port, RDC, RDC system, TDC, TXC, IPP, ZCP, MAC/XMAC/BMAC, FFLP, and multi-MAC state.

Core prototypes include `nxge_init()`, `nxge_uninit()`, diagnostic 64-bit get/put, PIO loop, and timer start/stop.

## Runtime Use

Driver attach allocates and initializes `nxge_t`, maps registers, configures DMA rings and classifier state, registers interrupts, exposes MAC rings/groups, creates kstats, and uses the parameter model for ndd/configuration interfaces. Runtime paths update statistics and use the ring/group/share structures for normal and hybrid I/O operation.

## Dependencies

Includes `nxge_mac.h`, `nxge_ipp.h`, and `nxge_fflp.h`, which provide many referenced types and constants. It also relies on MAC framework, DDI, kstat, DMA, MII, and platform-specific types from surrounding includes.

## Risks and Invariants

The loopback enum explicitly warns not to reorder values because driver code depends on order.

`nxge_t` is a large shared state structure with many locks and subsystem-owned fields. Changes require understanding attach/detach, interrupt, DMA, MAC, FMA, and hybrid-I/O interactions.

Array dimensions such as `NXGE_MAX_TDCS`, `NXGE_MAX_RDCS`, `NXGE_MAX_RDC_GROUPS`, and `NXGE_MAX_VRS` must remain consistent with hardware and included headers.

Diagnostic ioctls expose powerful low-level operations such as register writes, resets, TCAM writes, and error injection; callers must be privileged and state-aware.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common.h

## Purpose

`nxge/nxge_common.h` defines common Neptune/NIU DMA, classification, partition, and hardware-resource configuration structures shared by nxge driver components.

## Main Interfaces

The header defines default per-port RX/TX DMA channel counts for NIU and Neptune, RDC group counts, timer constants, and descriptor/ring sizing defaults. Several defaults vary by platform, endian, architecture, and NIU workaround macros.

`nxge_rdc_cfg_t` describes a receive DMA channel: partitioning/logical-page setup, WRED parameters, mailbox address, header mode, buffer offsets and block sizes, RBR/RCR addresses and lengths, completion thresholds/timeouts, logical-device group, event masks, and address mode.

`nxge_tdc_cfg_t` describes a transmit DMA channel: partitioning/logical-page setup, transmit ring address/length, mailbox, logical-device group, event mask, reclaim threshold, packet counter, and last mark.

`nxge_tdc_grp_t` and `nxge_rdc_grp_t` describe transmit and receive DMA channel groups, including start channel, max count, bitmap, default RDC, config method, and logical group index. Bit macros manipulate RDC/DC maps.

`nxge_dma_pt_cfg_t` is per-port DMA configuration: MAC port, hardware properties, buffer/ring sizes, TX map, TDC/RDC groups, per-RDC interrupt thresholds/timeouts, full-header flag, and RX DRR weight.

`nxge_class_pt_cfg_t` configures MAC/VLAN classification tables, hash initializers, multicast/default group mapping, and TCAM class config values.

`nxge_common_t` stores per-device shared common resources such as partition id, 32-bit mode, all RDC/TDC configs, DMA common config, timer resolution, system-error owner, layer 2/3/4 classifier EtherTypes, and hash initial values.

`nxge_part_cfg_t` models partition/logical-domain configuration: RDC/TDC maps, per-port configs, flow classification partitioning, and service/read-write/read-only attributes.

`nxge_hw_list_t` is the per-hardware shared state object containing locks, parent device pointer, per-function `nxge_t` pointers, device count, flags, hardware/platform type, transceiver addresses, HIO/TCAM pointers, TCAM size, and programmable L2/L3 class tracking.

## Runtime Use

Driver initialization reads platform/firmware properties into these structures, allocates DMA resources, configures hardware rings/groups, partitions resources across ports or domains, and uses classification maps to steer traffic to RDC groups.

## Dependencies

The header relies on many constants and types from nxge hardware, DMA, classifier, and platform headers included before it by nxge components.

## Risks and Invariants

Ring size defaults are highly conditional. Changing macros can alter DMA memory footprint and hardware programming on specific platforms.

The bitfield structures `nxge_param_map_t` and `nxge_rcr_param_t` have separate big- and little-endian layouts; serialized or register-facing use must preserve endian semantics.

Resource maps and group indexes must stay within hardware maxima. Incorrect partition maps can assign the same DMA channel or classification resource to multiple owners.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common_impl.h

## Purpose

`nxge/nxge_common_impl.h` provides implementation-side OS abstraction macros, debug bit definitions, PIO/register access helpers, FMA wrappers, and tracing-aware register read/write macros for the nxge driver and NPI layer.

## Main Interfaces

`NPI_REGH()` and `NPI_REGP()` extract register handle and mapped register pointer from an NPI handle. `__NXGE_STATIC` and `__NXGE_INLINE` expand differently when DMA/TXC debug builds need externally visible helpers.

The header defines a large `nxge_debug_level` bitmask space, including subsystem bits for metadata, RX, TX, OBP, VPD, DDI, memory, SAP, ioctl, module, DMA, STREAMS, interrupts, system errors, kstats, PCS/MII/MIF/FCRAM/MAC/IPP, secondary paths, NDD, TCAM, config, virtualization, HIO, notes, error control, and dump-always. NPI debug flags cover RDC, TDC, TXC, IPP, PCS/MAC/ZCP/TCAM/FCRAM/FFLP/VIR/PIO/VIO/register/control/error areas.

It includes DDI and Ethernet headers, maps NXGE mutex/rwlock/allocation/delay macros to illumos kernel primitives, and typedefs OS-facing types for mutexes, rwlocks, devinfo, interrupt cookies, access handles, DMA handles, and free routines.

PIO macros wrap `ddi_get*()`/`ddi_put*()` for general device offsets, NPI register offsets, and memory-style mapped register access. Some 64-bit NPI access macros cast offsets on i386.

FMA macros wrap DDI service/fault constants and fault-report/check helpers. Register read/write macros optionally record trace/show output under `REG_TRACE` or `REG_SHOW`.

## Runtime Use

Driver code uses these macros to centralize register I/O, synchronization, memory allocation, fault reporting, debug logging, and trace instrumentation. Build flags can compile in additional tracing or expose static functions for debugging.

## Dependencies

Includes `sys/types.h`, `sys/ddi.h`, `sys/sunddi.h`, `sys/dditypes.h`, and `sys/ethernet.h`. Depends on nxge and NPI types defined by surrounding driver headers.

## Risks and Invariants

Register access macros evaluate arguments directly and perform typed pointer arithmetic on mapped register bases; incorrect offsets or widths can cause hardware faults or corrupt device state.

`NXGE_PIO_WRITE16` appears to call `ddi_get16()` with a write-like argument list instead of `ddi_put16()`. If used, that macro would be wrong or fail to compile; it may be unused or masked by other access paths.

Debug and trace macros can materially change visibility and side effects. Code relying on `__NXGE_STATIC` behavior must account for debug builds.

FMA wrappers assume `nxgep` has valid `dip` and register handles; using them during partial attach/detach needs state checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common_impl.h -->