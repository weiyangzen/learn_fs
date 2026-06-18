# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_eckd.h

## Purpose
This header defines the ECKD-specific command codes, controller order/suborder constants, packed channel-program payloads, Read Subsystem Data payloads, ESE extent-pool records, CUIR/OOS attention messages, PPRC/host-access records, DSO release-space records, and PAV alias management structures shared by the ECKD discipline and alias code.

## Important APIs, Types, and Functions
The first section enumerates ECKD CCWs such as READ/WRITE, DEFINE EXTENT, LOCATE RECORD, LOCATE RECORD EXTENDED, PREFIX, READ CONFIGURATION DATA, READ SUBSYSTEM DATA, SENSE SUBSYSTEM STATUS, RESERVE/RELEASE, and DSO. PSF and DSO order constants cover PRSSD, CUIR response, SSC, Query Host Access, PPRC Extended Query, Volume Storage Query, Logical Configuration Query, and Release Allocated Space.

Core packed channel payloads are `struct eckd_count`, `struct ch_t`, `struct chr_t`, `struct DE_eckd_data`, `struct LO_eckd_data`, `struct LRE_eckd_data`, and `struct PFX_eckd_data`. Device and configuration records are represented by `struct dasd_eckd_characteristics`, `struct dasd_ned`, `struct dasd_sneq`, `struct vd_sneq`, `struct dasd_gneq`, `struct dasd_conf_data`, and `struct dasd_conf`. Subsystem query records include `struct dasd_rssd_features`, `struct dasd_rssd_messages`, `struct dasd_rssd_vsq`, `struct dasd_ext_pool_sum`, `struct dasd_rssd_lcq`, `struct dasd_psf_query_host_access`, and `struct dasd_psf_prssd_data`. ESE release-space payloads use `struct dasd_dso_ras_data` and `struct dasd_dso_ras_ext_range`.

PAV/alias state is defined by `enum pavtype`, `struct alias_root`, `struct alias_server`, `struct alias_lcu`, `struct alias_pav_group`, `struct summary_unit_check_work_data`, and `struct read_uac_work_data`. `struct dasd_eckd_private` is the ECKD discipline's per-device private state. External hooks declared here connect to alias code and ECKD I/O reset helpers.

## Control Flow
The header has no executable control flow, but its structures dictate the binary layout consumed by `dasd_eckd.c`. Define Extent and Locate Record payloads are filled before READ/WRITE/FORMAT CCWs. Prefix payloads combine Define Extent and Locate Record Extended data and carry PAV base verification bits. PSF PRSSD payloads precede RSSD reads for feature, message, host-access, PPRC, volume-storage, and logical-configuration queries. CUIR and OOS structures are interpreted after RSSD message-buffer reads. Alias structures organize devices by storage server, LCU, and PAV group so path and alias operations can walk related devices.

## State and Persistence
Most definitions are packed views over hardware, firmware, or channel-program memory and do not store state by themselves. The persistent in-memory state carrier is `struct dasd_eckd_private`: it caches device characteristics, configuration-data pointers, analyzed count records, CDL status, cache attributes, features, ESE metadata, UID, alias/LCU links, active request count, zHPF max data size, and summary-unit-check reason. The controller-visible data represented by these structures can outlive one kernel request, but the header itself provides no persistence policy.

## Dependencies and Integration Points
The header assumes Linux kernel integer types, list/completion/workqueue types, and DASD core types are available through includers. It is tightly coupled to IBM storage-controller ECKD layouts, s390 channel command encoding, DASD alias management, and the generic DASD UID/copy/path abstractions. Its exported declarations are consumed by `dasd_eckd.c`, ECKD alias-management code, and any code needing to reset alias-built channel programs back to base-device I/O.

## Risks and Test Signals
The main risks are binary layout drift and bitfield ambiguity. Almost every hardware-facing structure is `packed`, so field order, size, endian assumptions, and bit meanings must match the architecture specification. Incorrect constants can produce invalid channel programs or misinterpret subsystem messages. Alias structures mix locks, lists, completions, and request pointers, so changes must preserve lifetime and lock assumptions in the implementation. Test signals are compile-time size/layout coverage where available, successful RCD/RSSD/PSF/DSO command execution, correct UID generation from NED/GNEQ/SNEQ data, CUIR/OOS message parsing, host-access output sanity, and PAV alias grouping behavior under path changes.
