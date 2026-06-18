<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h -->
# sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h

## Purpose
Defines the PDS core PCI device-command ABI and BAR0 register layout. This is the low-level firmware interface for device identify/init/reset, firmware download/control, SR-IOV VF management, status codes, and hardware info/command registers.

## Important APIs, Types, And Functions
- PCI and BAR constants identify Pensando/AMD devices, BAR offsets for device info, command registers, command data, interrupt status/control, and the doorbell BAR.
- `enum pds_core_cmd_opcode` defines device-command opcodes: NOP, IDENTIFY, RESET, INIT, FW_DOWNLOAD, FW_CONTROL, VF_GETATTR, VF_SETATTR, and VF_CTRL.
- `enum pds_core_status_code` maps firmware return codes such as success, invalid opcode, permission, no memory, busy, bad firmware, no client, and broken PCI status.
- `struct pds_core_drv_identity` and `struct pds_core_dev_identity` exchange driver identity and device capabilities including LIF, interrupt, doorbell, coalescing, and VIF type counts.
- Device command structures cover identify, reset, init, firmware download/control, VF attributes, and VF start control.
- `union pds_core_dev_cmd` is fixed at 64 bytes, `union pds_core_dev_comp` at 16 bytes.
- `struct pds_core_dev_info_regs`, `pds_core_dev_cmd_regs`, and `pds_core_dev_regs` describe the 4 KiB BAR0 page, including read-only device info and read/write command registers.

## Control Flow
The driver maps BAR0, verifies `PDS_CORE_DEV_INFO_SIGNATURE`, prepares `cmd_regs->cmd` and optional `cmd_regs->data`, writes the command doorbell, polls `done` for `PDS_CORE_DEV_CMD_DONE` within `PDS_CORE_DEVCMD_TIMEOUT`, then reads the typed completion. Identify and init exchange side data through the command data area. Firmware update flows download chunks by DMA address/offset/length, then issue firmware-control install/activate/status operations. VF management sends get/set/control commands with VF indexes and selected attributes.

## State And Persistence
Persistent device state includes firmware status/heartbeat/generation, serial and firmware version, hardware timestamp registers, initialized device/LIF/VF state, firmware slots, VF attributes, and active boot slot. Command register contents are transaction state. Static assertions enforce register-page sizes and ABI struct sizes.

## Dependencies And Integration Points
This header integrates the PCI core driver with firmware, SR-IOV management, firmware update tooling, interrupt setup, and the AdminQ layer that is initialized after the device-command path. It uses Linux endian types, packed layout annotations, and PCI IDs.

## Risks And Edge Cases
Key risks are BAR offset/layout drift, command register races if callers do not serialize devcmd access, timeout handling during firmware restart, endian conversion mistakes, invalid firmware slot transitions, DMA buffer/address errors during firmware download, VF attribute union misuse, and stale firmware generation after reset. The fixed data area size means identity structures must remain within the asserted 1912-byte limit.

## Test Signals
Signals include BAR signature validation, identify/init/reset on supported devices, firmware heartbeat/generation change detection, firmware download/install/activate/status tests, VF MAC/VLAN/rate/trust/spoof/link attributes, VF start-all/start flows, static assertion builds, and fault injection for timeout or `PDS_RC_BAD_PCI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pds/pds_core_if.h -->
