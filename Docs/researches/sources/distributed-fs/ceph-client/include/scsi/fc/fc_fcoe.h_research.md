# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcoe.h

Purpose: Defines Fibre Channel over Ethernet frame, trailer, MAC mapping, and link-error status structures.

Important APIs/types/functions: Constants include default FC-MAP OUI, non-FIP FLOGI MAC, version, header lengths, and minimum frame sizes. `struct fcoe_hdr` contains version/reserved/SOF fields. `struct fcoe_crc_eof` stores CRC and EOF trailer. `struct fcoe_fc_els_lesb` records FCoE link error counters. `fc_fcoe_set_mac()` writes OUI plus FC destination ID into a MAC address.

Control flow and state: Stateless helpers encode/decode FCoE header version and map FC IDs to Ethernet MAC addresses.

Dependencies and integration: Used by FCoE low-level drivers, libfc frame handling, and FCoE sysfs LESB reporting.

Risks and test signals: Risks include version nibble mistakes, MAC mapping errors, trailer packing mismatch, and host/network-endian counter display confusion. Tests should cover MAC generation, header/trailer lengths, version macros, and LESB counter export.
