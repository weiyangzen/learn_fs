# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic_v3_its.c

## Purpose
This guest ITS helper programs GICv3 ITS tables and command queue entries for MSI/LPI-oriented KVM arm64 tests. It is derived from kernel ITS driver logic but scoped to selftest needs.

## Important APIs, Types, and Functions
`its_init()` installs collection, device, and command queue tables and enables the ITS. `struct its_cmd_block` represents a 32-byte command. Command helpers include `its_send_mapd_cmd()`, `its_send_mapc_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`. Encoding helpers fill device IDs, event IDs, physical INTIDs, ITT addresses, target redistributors, collections, size, and valid bits.

## Control Flow
Initialization finds BASER registers by type, writes table attributes, writes CBASER, then sets `GITS_CTLR_ENABLE`. Command submission reads `GITS_CWRITER`, writes the command into the guest command queue, orders it with `dsb(ishst)`, advances CWRITER, and optionally polls CREADR.

## State, Dependencies, and Integration
The file operates on guest memory supplied by tests and fixed ITS MMIO base mappings from `vgic_its_setup()`. It depends on GICv3 register definitions, relaxed MMIO accessors, endian conversion, and KVM's synchronous ITS emulation assumption.

## Risks and Test Signals
The poll iteration count is zero because current KVM processes commands synchronously; asynchronous emulation would immediately assert. Wrong table sizing, alignment, or BASER type discovery causes guest failures or missing LPI delivery.
