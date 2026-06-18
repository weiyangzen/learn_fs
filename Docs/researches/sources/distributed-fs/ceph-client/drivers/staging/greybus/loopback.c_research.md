# sources/distributed-fs/ceph-client/drivers/staging/greybus/loopback.c

## Purpose
Greybus loopback test/load driver. It exposes sysfs controls and debugfs latency output for generating ping, transfer, and sink loopback traffic synchronously or asynchronously over a Greybus connection.

## Important APIs, Types, And Functions
`struct gb_loopback` stores the connection, class device, debugfs file, latency FIFO, mutex, worker thread, wait queues, outstanding async count, statistics, test parameters, counters, timeouts, and latency tags. `gb_loopback_operation_sync()` and `gb_loopback_async_operation()` send operations. Type-specific helpers handle ping/transfer/sink. `gb_loopback_fn()` is the traffic-generating kthread. `gb_loopback_request_handler()` responds to loopback requests from the peer.

## Control Flow
Module init creates a debugfs root, class, and Greybus driver. Probe validates one loopback CPort, creates/enables the connection, creates a class device with sysfs attributes, allocates the latency FIFO, starts the worker thread, increments global device count, enables latency tags, and drops runtime PM. Writing sysfs attributes resets counters and wakes the worker when type is valid. The worker holds PM while active, sends configured operations until iteration limits, updates stats, and sleeps between sends if requested.

## State And Persistence
State is per connection and visible through sysfs: type, size, wait, iteration counts, async flag, timeout, outstanding max, errors, and computed min/max/avg stats. Debugfs exposes raw latency samples consumed from a FIFO. No on-disk state persists.

## Dependencies And Integration Points
Uses Greybus loopback protocol, operation latency tags, Linux kthreads, wait queues, atomics, kfifo, debugfs, sysfs class devices, runtime PM, and IDA.

## Risks
Complex async lifetime: callbacks own operation references and decrement outstanding counts while disconnect disables the connection and stops the thread. Sysfs parsing uses broad integer scans and clamps only some fields. Latency/stat arithmetic must guard divide-by-zero and wraparound.

## Test Signals
Exercise sync/async ping, transfer data verification, sink, iteration completion, infinite mode, outstanding throttling, timeout accounting, debugfs FIFO reads, sysfs clamping, remote loopback request handling, disconnect with in-flight async operations, and registration failure paths.
