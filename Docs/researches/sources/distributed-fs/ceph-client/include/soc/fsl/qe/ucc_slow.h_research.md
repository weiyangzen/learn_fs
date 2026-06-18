# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc_slow.h

Purpose: declares Slow UCC descriptor bits, configuration enums, private state, and lifecycle/control APIs for lower-speed QE serial protocols.

Important APIs and types: TX/RX BD macros cover ready/empty, wrap, interrupt, first/last, address/control, CRC, continuous, preamble, heartbeat, underrun, CTS/carrier/collision, frame length, non-octet, parity, abort, CRC, overrun, and address-match conditions. Alignment constants define RX/MRBLR/parameter-RAM constraints. Enums configure QMC/UART/BISYNC mode, transparent CRC, TX/RX oversampling, NRZ/NRZI encoding, and diagnostic loopback/echo. `struct ucc_slow_info` carries UCC number, protocol, clocks, register address, IRQ, masks, BD ring lengths, mux flags, inversion/encoding/timing options, max RX length, CRC, mode, and diagnostics. `struct ucc_slow_private` tracks mapped registers/pram, BD rings, queue/list state, event/mask pointers, saved mask, enabled/stopped flags, RX accumulation, and optional stats. APIs initialize/free, enable/disable, graceful/force stop TX, restart TX, and compute command subblocks.

Control flow: a protocol driver initializes parameter RAM and BD rings, enables selected directions, processes RX/TX BDs and events, uses QE commands for stop/restart, then frees resources.

State and persistence: state is runtime parameter RAM, BD rings in MURAM, queued TX confirmations, RX accumulation, event masks, and counters. No persistent data.

Dependencies and integration points: includes QE/immap/common UCC headers and list support via included structures. Used by UART, BISYNC, QMC, and related slow protocols.

Risks and test signals: risks include BD flag aliasing across protocols, ring wrap errors, RX frame accumulation leaks, stop/restart races, parameter RAM alignment mistakes, and missed IRQ masking. Test UART/QMC/BISYNC configurations, RX/TX rings, graceful/force stop, restart, error BD handling, and teardown with queued frames.
