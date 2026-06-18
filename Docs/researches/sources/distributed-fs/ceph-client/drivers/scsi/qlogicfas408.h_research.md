# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.h

## Purpose
`qlogicfas408.h` defines the shared configuration, private state, register-bank macros, and exported function prototypes for QLogic FAS408-compatible SCSI controller support. It is the contract between the low-level FAS408 engine and board-specific wrappers.

## Important APIs, Types, And Functions
`struct qlogicfas408_priv` is the key host-private structure and contains I/O base, initiator ID, abort/reset flag, IRQ, interrupt type, info buffer, active `scsi_cmnd`, host pointer, and linked-list pointer. Configuration macros include `QL_TURBO_PDMA`, `QL_ENABLE_PARITY`, `QL_RESET_AT_START`, `XTALFREQ`, `SLOWCABLE`, `FASTSCSI`, `FASTCLK`, `SYNCXFRPD`, `SYNCOFFST`, and `WATCHDOG`. `REG0` and `REG1` switch the chip register map using `qbase` and `int_type`. `get_priv_by_cmd()` and `get_priv_by_host()` retrieve private state from SCSI objects. The prototypes expose queueing, interrupt, BIOS geometry, abort/reset, setup, detect, chip-type, and interrupt-disable routines.

## Control Flow
The header has no executable flow by itself, but the `REG0`/`REG1` macros have side effects: they read and write adapter registers to switch register banks. Callers must have local variables named `qbase` and, for `REG1`, `int_type`, matching the macro assumptions.

## State And Persistence
Compile-time macro choices control runtime hardware programming. `struct qlogicfas408_priv` is volatile per-host state allocated inside `Scsi_Host` private storage. No persistent state is defined.

## Dependencies And Integration Points
The header depends on Linux SCSI types such as `struct scsi_cmnd`, `struct scsi_device`, `struct Scsi_Host`, `struct gendisk`, and `sector_t`, plus port I/O helpers through the C files that include it. It integrates the shared implementation with `qlogicfas.c` and any PCMCIA wrapper that uses the same function exports.

## Risks And Edge Cases
The register-bank macros are statement-expression-like comma expressions with hidden local-variable dependencies, making misuse easy during refactoring. Many configuration settings are compile-time constants rather than module parameters, so board-specific timing, parity, and reset behavior require rebuilds. `get_priv_by_cmd()` assumes the SCSI command and device/host links are valid. `WATCHDOG` is described as microseconds but used by the implementation as a jiffies delta, which is a documentation or unit mismatch to keep in mind.

## Test Signals
Build coverage should include all wrappers that include this header. Runtime signals are correct private-state retrieval, successful register-bank switching under both ISA-style `INT_TYPE = 2` and PCMCIA-style `0`, expected behavior when toggling parity/reset/sync macros, and no compile regressions when prototypes are used by external board drivers.
