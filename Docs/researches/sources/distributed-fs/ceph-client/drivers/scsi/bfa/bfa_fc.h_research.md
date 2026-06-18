# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fc.h

## Purpose
`bfa_fc.h` is the Fibre Channel protocol wire-format header. It defines packed frame headers, ELS/BLS payloads, login/service parameter layouts, FCP command and response IUs, CT generic service headers, name-server and management-server request/response payloads, FDMI records, well-known addresses, timeout constants, virtual fabric tags, speed enums, and utility types such as `wwn_t`, `mac_t`, and `fc_symname_s`.

## Important APIs and Types
Foundational structs include `struct fchs_s` for FC frame headers, `fc_els_cmd_s`, `fc_logi_s`, `fc_logo_s`, `fc_adisc_s`, `fc_prli_s`, `fc_prlo_s`, `fc_scr_s`, `fc_ls_rjt_s`, `fc_rrq_s`, `fc_ba_acc_s`, `fc_tprlo_s`, `fc_rscn_pl_s`, `fc_rnid_*`, `fc_rpsc*`, `fcp_cmnd_s`, `fcp_resp_s`, `ct_hdr_s`, FC-GS name-server structs, GMAL/GFN structs, and FDMI attribute/register structs. Enums and macros define routing, category, FC types, frame-control bits, ELS opcodes, PDU size bounds, LS reject reasons, CT responses/reasons, FC-GS commands, FC classes, FCP IO directions, and task management flags.

## Control Flow and State
This header has no executable flow, but its field layouts are consumed by `bfa_fcbuild.c` to construct login, discovery, name-server, management-server, accept, and reject frames. Parse helpers validate these layouts by checking command codes, PRLI response codes, target/initiator bits, PLOGI class validity, receive size ranges, and WWN identity.

## State and Persistence Behavior
The data is primarily transient wire state. Some fields represent persistent identifiers or management information, including WWNs, symbolic names, FDMI HBA/port attributes, RNID topology data, fabric names, and management addresses. Packed layout and bitfield endian branches are part of the on-wire ABI and must remain stable.

## Dependencies and Integration Points
It depends on `bfad_drv.h` for Linux integer, endian, `BIT`, and SCSI LUN types. It is included by base definitions, FCS definitions, and frame-building code. Fibre Channel control modules use it to interpret unsolicited frames and build FCXP payloads.

## Risks and Test Signals
Risks include bitfield layout differences across endian/compilers, missing byte-order conversion for 24-bit IDs or `__be*` fields, flexible array sizing mistakes, duplicated RNID associated-type macros, and unsafe payload length assumptions. Test signals include protocol frame golden tests for ELS, BLS, CT, FCP, RSCN, RNID, RPSC, FDMI, and name-server packets on little- and big-endian builds.
