# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fip.h

Purpose: Defines FCoE Initialization Protocol headers, opcodes, subcodes, flags, multicast MACs, timing constants, and descriptors for fabric, VLAN, VN2VN, and encapsulated ELS/ILS exchanges.

Important APIs/types/functions: `struct fip_header` is the common packet header. Descriptor types include priority, MAC, FC-MAP, WWN/name, fabric, FCoE size, encapsulated frame, VN ID, keep-alive, VLAN, FC-4 features, and vendor descriptors. Enums define discovery, link-service, control, VLAN, VN2VN subcodes, and flags such as FPMA/SPMA, FCF/FDF, availability, solicited, and F-port.

Control flow and state: This header is format-only. FIP controllers use the constants to discover FCFs, negotiate VLANs, maintain keep-alives, process VN2VN probes/claims/beacons, and carry FLOGI/FDISC/LOGO/ELP payloads.

Dependencies and integration: Depends on FC name-server types and Ethernet address lengths. Used by fcoe controller code and sysfs FCF device representation.

Risks and test signals: Risks include descriptor length unit mistakes, packed layout/alignment errors, subcode/opcode confusion, malformed descriptor tolerance, and keep-alive timing bugs. Tests should parse/build FIP discovery, VLAN notification, VN2VN claim, FLOGI encapsulation, and descriptor fuzz cases.
