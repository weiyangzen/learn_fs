# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-ipd-defs.h

## Purpose
`cvmx-ipd-defs.h` is the CSR definition file for the Octeon Input Packet Data unit. IPD receives packets from packet interfaces, allocates WQEs and packet buffers, applies backpressure and RED policy, tracks FIFO pointer state, and reports packet/input errors.

## Important APIs, Types, And Functions
Address macros define buffer skip/back-pointer sizing, packet buffer size, WQE FPA pool, control status, BIST, interrupt enable/sum, pointer FIFO controls and valid pointers, port backpressure counters, RED thresholds and enable bits, QoS counters/marks, BPID counters, SOP state, credits, request weights, sub-port state, and packet error registers. The union families mirror these groups: skip/back unions, `cvmx_ipd_ctl_status`, BIST, ECC, FIFO controls, interrupt status, pointer-valid registers, per-port counters, RED/QoS, and WQE FPA selection.

## Control Flow
The header contains no functions. `cvmx-ipd.h` and helper implementations compose these unions and write CSRs to configure receive buffer layout, caching mode, backpressure, WQE allocation, and RED policy. Shutdown paths read pointer count and FIFO control registers to drain prefetched buffers.

## State And Persistence
All state is hardware state in the IPD block: enable/reset, buffer sizing, FIFO pointers, in-flight prefetched buffers, packet counters, backpressure/RED thresholds, interrupt latches, and error status. Misprogramming these values affects every incoming packet path.

## Dependencies And Integration Points
The definitions are included by `cvmx-ipd.h` and used by packet helper initialization, FPA pool management, PIP/PIP reset, interrupt handlers, RED setup, and receive buffer reclamation. They rely on `CVMX_ADD_IO_SEG`, bitfield layout, and Octeon model feature checks in callers.

## Risks
Many macros mask offsets, so invalid ports or queues can alias. Buffer skip, back-pointer, and size fields must agree with FPA pool object sizes and WQE layout; mistakes can corrupt packet memory. Some pointer FIFO registers require `cena`/`raddr` sequencing. Interrupt/status fields vary across chip families.

## Test Signals
Validate IPD configuration by receiving packets of varying sizes, checking WQE and buffer pointer layout, exercising backpressure and RED thresholds, draining/freeing IPD during shutdown without FPA leaks, and inspecting interrupt/error counters under malformed packet tests.
