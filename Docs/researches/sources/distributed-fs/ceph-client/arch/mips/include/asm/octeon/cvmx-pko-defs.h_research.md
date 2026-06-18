# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pko-defs.h

## Purpose
`cvmx-pko-defs.h` is the generated CSR definition file for the Octeon Packet Output unit. It maps PKO configuration, queue pointers, queue QoS, port mapping, command buffers, CRC, debug, BIST, error, interrupt, rate/throttle, timestamp, loopback, queue mode, and engine storage/inflight registers.

## Important APIs, Types, And Functions
The file exports `CVMX_PKO_MEM_*` and `CVMX_PKO_REG_*` address macros. Memory-indexed logical register windows include `CVMX_PKO_MEM_QUEUE_PTRS`, `QUEUE_QOS`, `PORT_PTRS`, `PORT_QOS`, `IPORT_PTRS`, `IQUEUE_PTRS`, `COUNT0`, `COUNT1`, `PORT_RATE0`, `PORT_RATE1`, throttle, and many debug views. Control/status registers include `CVMX_PKO_REG_FLAGS`, `CMD_BUF`, `READ_IDX`, `GMX_PORT_MODE`, `QUEUE_MODE`, `ERROR`, `INT_MASK`, `BIST_RESULT`, `ENGINE_INFLIGHT`, `ENGINE_STORAGE`, `MIN_PKT`, loopback BPID/PKIND, preemption, queue pointer extension, throttle, and timestamp.

Important unions include `cvmx_pko_mem_queue_ptrs` and `cvmx_pko_mem_iqueue_ptrs` for queue-to-port, command-buffer pointer, tail/index, QoS mask, static priority, and static queue state; `cvmx_pko_mem_port_ptrs` for port-to-engine/backpressure mapping; `cvmx_pko_reg_cmd_buf` for FPA pool and command-buffer size; `cvmx_pko_reg_flags` for enable, reset, store endian, DWB, and throttle; `cvmx_pko_reg_error` and `cvmx_pko_reg_int_mask` for parity/doorbell/current-zero/loopback errors; and `cvmx_pko_mem_count0/count1` for packet and octet counters.

## Control Flow
No functions execute here. External PKO code uses `CVMX_PKO_REG_READ_IDX` to select an internal memory row, then reads or writes the `CVMX_PKO_MEM_*` data registers. Bring-up usually resets PKO, configures command-buffer pool and queue/port pointer tables, programs QoS and rate registers, enables PKO, and later reads counters/debug/error registers.

## State And Persistence
All state is in PKO hardware. Queue and port pointer tables persist active output routing and command-buffer ownership. Counters persist transmitted packet/octet counts. Error and BIST registers expose hardware health. Rate and throttle registers affect future scheduling. The unions are only typed overlays for 64-bit CSR values.

## Dependencies And Integration Points
The header depends on Octeon CSR infrastructure and endian bitfield selection. It is consumed by `cvmx-pko.h` and lower-level packet output initialization code, and it links to FPA buffer pools, command queues, GMX network ports, PCI/loopback output ports, and POW ordering when PKO locking is used.

## Risks
PKO internal memories are selected indirectly through `REG_READ_IDX`, so stale or wrong indices can read or clear the wrong port/queue counters. Queue pointer fields control command-buffer ownership; corrupt values can lose packets or leak FPA buffers. Many debug unions have model-specific field alternatives, so portable code should avoid assuming one layout. Error/interrupt bit semantics are not encoded in the C type. Rate, throttle, and preemption fields can starve queues if programmed incorrectly.

## Test Signals
Strong signals include reset/BIST checks, address expansion tests, queue pointer table programming validation, packet transmit tests that increment `COUNT0` and `COUNT1`, error interrupt injection for parity/doorbell/current-zero paths, read-index selection tests, rate-limit behavior checks, and packet ordering tests across static-priority and weighted queues.
