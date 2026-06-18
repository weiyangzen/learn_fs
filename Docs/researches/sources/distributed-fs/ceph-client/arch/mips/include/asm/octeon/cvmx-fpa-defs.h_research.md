# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-fpa-defs.h

## Purpose
This header defines the CSR map and bitfield layouts for Octeon's Free Pool Allocator hardware. It covers pool sizes, marks, queue availability, page indices, pool start/end/thresholds, interrupts, BIST, address range errors, WART controls, and global FPA enable/reset state.

## Important APIs, Types, and Functions
Address macros include `CVMX_FPA_CTL_STATUS`, `BIST_STATUS`, `INT_ENB`, `INT_SUM`, per-pool `FPFX_MARKS/SIZE`, `QUEX_AVAILABLE`, `QUEX_PAGE_INDEX`, `POOLX_START_ADDR`, `POOLX_END_ADDR`, `POOLX_THRESHOLD`, packet/WQE thresholds, queue active/expected, address-range error, and `FPA_CLK_COUNT`. Unions expose global enable/reset/load/store behavior, memory error fields, FIFO read/write marks and sizes, queue available counts/page indices, pool threshold and address range fields, interrupt enable/summary bits for queue underflow/count-off/parity, pool threshold, free events, physical-address errors, and CN30XX/CN61XX/CN63XX/CN68XX-specific layouts including pool 8 support.

## Control Flow
No executable logic is present. FPA setup code writes pool start/end/threshold and FIFO mark/size CSRs, enables the allocator, then runtime allocation/free code uses FPA I/O addresses while diagnostics read availability and interrupt/error registers.

## State and Persistence Behavior
All state is in FPA hardware: pool ranges, free counts, FIFO marks, interrupt latches/enables, active/expected queue pointers, and global enable/reset bits. Counts change as blocks are allocated and freed. Error and threshold status persists until cleared according to hardware semantics.

## Dependencies and Integration Points
It depends on CSR address helpers and endian bitfield definitions. It is consumed by `cvmx-fpa.h`, FPA initialization/shutdown code, IPD/PKO packet buffer setup, command queue allocation, and interrupt/error reporting.

## Risks
FPA pool definitions are fundamental to packet and command-buffer memory safety. Wrong start/end/threshold values can allow out-of-range frees or allocator underflow. Interrupt unions have chip-specific variants; using the wrong view can miss pool8 or physical-address error bits. Some generated layouts contain duplicated-looking fields, so code should prefer known chip-specific definitions and avoid assuming reserved fields.

## Test Signals
Verify pool initialization, allocation/free counts, threshold interrupts, underflow/parity/count-off handling, pool range error reporting, pool 8 behavior on CN68XX-class hardware, and clean BIST status. Packet receive/transmit under memory pressure is an important integration signal.
