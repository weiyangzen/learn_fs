
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_fast.c

## Purpose
Implements the QE UCC Fast support library for clients such as Ethernet. It validates caller-supplied fast UCC configuration, maps UCC registers, allocates QE MURAM virtual FIFOs, programs GUMR/FIFO/interrupt/mux registers, and exports enable/disable/dump/on-demand/free helpers.

## Important APIs, Types, and Functions
- Exported: `ucc_fast_dump_regs()`, `ucc_fast_get_qe_cr_subblock()`, `ucc_fast_transmit_on_demand()`, `ucc_fast_enable()`, `ucc_fast_disable()`, `ucc_fast_init()`, and `ucc_fast_free()`.
- Uses `struct ucc_fast_info` as caller-provided configuration and returns `struct ucc_fast_private`.

## Control Flow
`ucc_fast_init()` validates UCC number, MRBLR alignment, and FIFO thresholds/alignment; allocates private state; ioremaps registers; sets fast type; builds GUMR from flags; allocates Tx/Rx virtual FIFO blocks from MURAM; writes FIFO registers; configures grant/breakpoint/TSA and clock/sync muxing; writes interrupt mask; clears pending events; and returns the initialized private object. Failure paths call `ucc_fast_free()`.

## State and Persistence
State is split between allocated `struct ucc_fast_private`, ioremapped UCC registers, MURAM FIFO offsets, and enabled flags. `ucc_fast_free()` releases MURAM and unmaps registers. Hardware configuration persists until changed or reset.

## Dependencies and Integration Points
Depends on QE MURAM allocation, shared UCC mux helpers, QE register layout, and caller-owned `ucc_fast_info`. TSA mode branches into TDM clock/sync configuration; NMSI mode uses direct UCC Rx/Tx clock muxing.

## Risks
- The caller owns `ucc_fast_info`; it must outlive the private object.
- Register/MURAM allocation order makes cleanup correctness important; partial failures rely on sentinel offsets initialized to `-1`.
- Invalid clock mappings are detected late, after register and MURAM work, but cleanup handles them.

## Test Signals
Alignment/threshold validation, allocation failure at each step, NMSI and TSA clock paths, enable/disable register bit changes, transmit-on-demand write, dump coverage, and leak checks around repeated init/free are useful.
