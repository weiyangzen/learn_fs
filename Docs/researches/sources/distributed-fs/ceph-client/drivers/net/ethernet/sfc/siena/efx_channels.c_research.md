# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx_channels.c

## Purpose
Manages interrupt mode selection, MSI-X/MSI/legacy resources, channel allocation, event queues, XDP TX queue placement, queue resizing, channel start/stop, and NAPI polling.

## Important APIs and functions
Public functions include interrupt probe/remove/enable/disable, affinity set/clear, event queue start/stop, channel init/probe/set/realloc/remove/fini/start/stop, NAPI init/fini, and dummy channel ops. Internal helpers compute RSS parallelism, allocate MSI-X channels, probe/init/remove event queues, copy channels for resize, assign XDP TX queues, process event queues, and adapt IRQ moderation.

## Control flow
Interrupt probing prefers MSI-X, falls back to MSI then legacy when allowed. MSI-X sizing accounts for RX/TX channels, separate TX channels, extra channels, and XDP dedicated/shared/borrowed modes. Channel probing creates event queues, TX queues, and RX queues in reverse order to preserve buffer table placement. NAPI polling processes event queues, flushes RX packets, refills descriptors, updates BQL, delivers skb lists, flushes XDP, and acknowledges events.

## State and persistence behavior
Maintains `n_channels`, RX/TX counts, channel offsets, XDP queue lookup, IRQ numbers, event queue state, NAPI state, queue indices, adaptive moderation counters, and active queue counts. No disk persistence.

## Dependencies
Depends on PCI MSI APIs, CPU topology masks, NAPI, TX/RX modules, NIC event callbacks, MCDI async mode switching, RFS, SR-IOV constraints, and XDP flush behavior.

## Risks
Resource accounting across MSI-X vectors, VIs, XDP queues, and separate channels is complex. Reallocation must preserve non-copyable channel buffer table entries and roll back safely. Interrupt teardown must synchronize IRQs before event queue destruction. Memory barriers protect event queue enabled state.

## Test signals
MSI-X/MSI/legacy fallback, RSS CPU settings, separate TX channels, XDP queue modes, ring resize rollback, ifup/ifdown loops, NAPI traffic, RFS expiry, interrupt affinity, and reset under traffic.
