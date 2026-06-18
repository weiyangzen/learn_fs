
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_slow.c

## Purpose
Implements the QE UCC Slow support library for UART/serial-like clients. It sets UCC slow mode, allocates PRAM and BD rings in QE MURAM, initializes GUMR and function-code registers, configures muxing/clocks, issues QE init commands, and exports Tx control and enable/disable helpers.

## Important APIs, Types, and Functions
- Exported: `ucc_slow_get_qe_cr_subblock()`, `ucc_slow_graceful_stop_tx()`, `ucc_slow_stop_tx()`, `ucc_slow_restart_tx()`, `ucc_slow_enable()`, `ucc_slow_disable()`, `ucc_slow_init()`, and `ucc_slow_free()`.
- Caller input is `struct ucc_slow_info`; output is `struct ucc_slow_private`.

## Control Flow
`ucc_slow_init()` validates input, maps registers, allocates PRAM and BD rings, assigns PRAM page to device with `qe_issue_cmd()`, switches UCC type to slow, initializes Rx/Tx BDs with wrap bits, programs GUMR_H/L, BMR/rbase/tbase, configures grant/breakpoint/TSA and NMSI clocks, writes interrupt masks, clears events, issues the requested QE init command, and returns private state. Free releases MURAM and unmaps registers.

## State and Persistence
Private state tracks PRAM, BD base offsets, register pointers, lists, and enabled flags. Hardware state persists in UCC registers and MURAM until reset/free. There is no file persistence.

## Dependencies and Integration Points
Depends on QE command engine, MURAM allocator, UCC mux helpers, and UCC slow register definitions. Clients typically own buffer management above the initialized BD rings.

## Risks
- Caller-owned configuration lifetime is required.
- `qe_issue_cmd()` return values are not checked in all control helpers, so command failures may be silent.
- NMSI clock configuration has hard failure if either clock is invalid; TSA mode expects an external TSA configuration.
- Ring lengths are caller supplied and should be validated by callers beyond allocation success.

## Test Signals
Valid and invalid UCC numbers, MRBLR alignment with/without `rfw`, MURAM allocation failure, Tx/Rx init mode combinations, NMSI clock validation, graceful/stop/restart command issuance, and repeated init/free leak checks.
