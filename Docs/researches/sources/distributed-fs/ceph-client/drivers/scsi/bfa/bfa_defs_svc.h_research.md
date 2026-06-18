# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_svc.h

## Purpose
`bfa_defs_svc.h` defines service-level configuration, attributes, and statistics for IOCFC, firmware IO and port modules, QoS, BB credit recovery, FCoE, FCP initiator throttling and IO statistics, physical port state/configuration, LUN masking, trunking, vHBA, CEE/DCBX, and AEN event payloads. It is the large shared contract between firmware, HAL modules, and management consumers.

## Important APIs and Types
Core IOCFC structs are `bfa_iocfc_intr_attr_s`, `bfa_iocfc_fwcfg_s`, `bfa_iocfc_drvcfg_s`, `bfa_iocfc_cfg_s`, `bfa_fw_iocfc_stats_s`, and `bfa_iocfc_attr_s`; these are consumed by `bfa_core.c` for memory sizing, firmware config requests, config responses, and interrupt coalescing. Statistics structs cover firmware IO, target IO, port PHY/link state machines, FIP/FCoE, LPSM, FC exchange, trunk, adapter port, MAC/CT/RDS modules, and aggregate `bfa_fw_stats_s`. Port/user-visible contracts include `bfa_port_cfg_s`, `bfa_port_attr_s`, `bfa_port_link_s`, `bfa_port_fc_stats_s`, `bfa_port_eth_stats_s`, and `bfa_port_stats_u`.

## Control Flow and State
The header defines state enums that drive management and module logic: QoS online/offline/disabled, BBCR state and error reasons, port states, port topology/opmode/link reasons, LUN mask states, FEC state, trunk state/link state, and rport AEN events. IOCFC config fields determine how many queues, IO requests, FC exchanges, unsolicited buffers, rports, task requests, SG pages, SAN boot targets, and completion queue elements are created during `bfa_cfg_get_meminfo` and `bfa_iocfc_send_cfg`.

## State and Persistence Behavior
Several structs mirror persistent or firmware-owned state: driver and firmware resource configuration, LUN mask entries, physical port config, QoS bandwidth, BB_SCN/BBCR, FAA state, path timeout, queue depth, FCoE FCF data, CEE/DCBX remote attributes, and AEN history entries. Runtime counters are volatile but represent firmware and HAL health signals.

## Dependencies and Integration Points
It includes `bfa_defs.h`, `bfa_fc.h`, and `bfi.h`, so it binds base adapter definitions, FC wire contracts, and firmware message types. `bfa.h` exposes these structs through IOCFC APIs and macros. Port, FCP, CEE, QoS, trunk, rport, and management modules use these definitions for ioctl/sysfs/netlink-style reporting.

## Risks and Test Signals
Risks include ABI instability, packed layout mismatch, endian mistakes in fields marked `__be16`, duplicated `MAX_LUN_MASK_CFG`, large stats structs drifting from firmware, and config values exceeding firmware limits. Test signals are firmware config negotiation, interrupt coalescing set/get, queue depth/path timeout limits, LUN mask min-config behavior, port state/link reason reporting, QoS/BBCR transitions, FCoE/CEE stats, and AEN queue population.
