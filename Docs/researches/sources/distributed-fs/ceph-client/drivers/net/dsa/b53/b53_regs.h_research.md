# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_regs.h

Purpose: shared B53 register map, offsets, bit masks, shifts, and table encodings.

Important APIs/types/functions: macro groups cover control/status/management/MIB/PVLAN/VLAN/jumbo/EEE/CFP pages, port control/STP, switch mode, Broadcom headers, aging/mirroring, device IDs, VLAN table variants, ARL table/search formats, EAP, and EEE fields.

Control flow: no executable flow; common and transport code use macros to build page/register accesses and bit encodings.

State and persistence behavior: no software state; describes hardware register state.

Dependencies and integration points: bit helper macros via includers; included by B53 private/common/SerDes code.

Risks: variant-specific offsets are easy to mix up; multiword fields depend on transport width/endianness; `VTA_VID_HIGH_MASK_25` references an apparently undefined `VTA_VID_HIGH_S_25E` if ever used.

Test signals: compile all B53 variants, hardware smoke tests for major register groups, and static analysis for dead/misspelled macros.
