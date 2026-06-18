# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8_reg.h

Purpose: KSZ8-family register, bit-mask, table, PHY-emulation, MIB, ACL/PME/EEE, and chip-ID definitions.

Important APIs/types/functions: defines global switch controls, power management, port controls/status, PHY/link-md registers, indirect table selection, interrupts, VLAN/static/dynamic/MIB table layouts, PME/ACL fields, chip IDs, KSZ8463-specific PHY/PTP/configuration registers, queue/priority constants, common alias names, tail-tag bits, FID/table sizes, and MIB masks.

Control flow: no executable flow. `ksz8.c` and common chip data use these constants to program and interpret hardware.

State and persistence: no software state; identifies hardware state such as VLAN/ALU tables, MIB counters, power management, and per-port PHY control/status.

Dependencies and integration: included by `ksz8.c`; works with chip-specific masks/shifts/register arrays from `ksz_common`.

Risks and test signals: duplicated or overlapping variant definitions, alias constants hiding chip differences, suspicious self-referential `TABLE_LINK_MD` definition, and bit inversions. Test register-level behavior on KSZ88x3/KSZ87xx/KSZ8463, VLAN/FDB/MIB correctness, PHY emulation, and PME/ACL indirect access.
