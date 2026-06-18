# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/bpck6.c

## Purpose
Supports MicroSolutions BACKPACK Series 6 parallel-port IDE adapters using the newer PPC command/register protocol.

## Important APIs, Types, And Functions
Command helpers include `bpck6_send_cmd()`, byte data helpers, `bpck6_read_regr()`, `bpck6_write_regr()`, and `bpck6_wait_for_fifo()`. Bulk transfer callbacks implement software and EPP modes. `bpck6_open()`, `bpck6_deselect()`, `bpck6_connect()`, `bpck6_disconnect()`, `bpck6_test_port()`, `bpck6_probe_unit()`, and `bpck6_log_adapter()` handle adapter activation and detection. `mode_map[]` maps core modes to PPC modes.

## Control Flow
Probe validates the port, opens the PPC interface, selects a unit, chooses a supported transfer mode, and then leaves normal ATA register and block accesses to protocol callbacks. FIFO waits guard bulk transfers, and command prefixes alter read/write/register versus port access.

## State And Persistence
The selected PPC mode, unit, saved parallel-port state, and any protocol-private values live in `pi_adapter`. Hardware selection persists while the core keeps the parport claimed.

## Dependencies And Integration Points
Uses `pata_parport.h`, raw port IO, module registration, and the core's probe loop for modes and units.

## Risks And Edge Cases
FIFO wait timeout behavior is key to avoiding hangs. Series 6 command prefixes differ from Series 5, so false-positive probing would cause bad strobes. EPP word/dword paths depend on port alignment enforced by the core.

## Test Signals
Series 6 probe, mode mapping across UNI/BI/EPP modes, FIFO timeout injection, register echo, block reads/writes, unit deselect, and clean disconnect.
