# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/dstr.c

## Purpose
Implements the DataStor EP2000 parallel-to-IDE protocol with nibble, 8-bit, and EPP block transfer modes.

## Important APIs, Types, And Functions
`dstr_read_regr()` and `dstr_write_regr()` access command/control register spaces through DataStor strobe sequences. `dstr_read_block()` and `dstr_write_block()` implement modes 0-4, including EPP-16 and EPP-32 paths. `dstr_connect()` and `dstr_disconnect()` use the `CCP()` command preamble to enter and leave adapter mode. The `dstr` protocol advertises `epp_first = 2`.

## Control Flow
The core tests available modes, then normal ATA operations dispatch into register or block callbacks. Connect saves the parallel-port state and sends the EP2000 enable sequence; disconnect sends the disable sequence and restores the port.

## State And Persistence
Only saved port register values and the selected mode are persistent in `pi_adapter`. Adapter hardware state remains enabled while connected.

## Dependencies And Integration Points
Uses `pata_parport.h` IO helpers and the core `pi_protocol` registration path.

## Risks And Edge Cases
EPP paths assume an EPP-capable base address and count alignment. The custom enable/disable sequence is easy to break with delay changes. Like other protocols, it monopolizes the parport while the ATA host is active.

## Test Signals
Probe in modes 0-4, EPP base alignment rejection in the core, sector read/write in EPP-16/32, connect/disconnect state restore, and default register echo validation.
