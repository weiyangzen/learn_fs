# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic_common.h

Purpose: this header supplies architecture-neutral NIC helpers layered over `struct efx_nic_type`. It centralizes event, TX, RX, interrupt, DMA buffer, register, and stats dispatch for controller implementations.

Important APIs: inline helpers expose `efx_nic_rev()`, event access/presence checks, TX/RX descriptor address calculation, TX empty/push decisions, NIC-specific TX/RX/event queue probe/init/remove/write calls, sensor events, recycle-ring sizing, monotonically safe diff stats, interrupt self-test accessors, and atomic stats update dispatch. It declares generic buffer, register, stats, interrupt, and TSO helpers implemented elsewhere.

Control flow and integration: callers in datapath and lifecycle code use these wrappers so common code stays independent of EF10/EF100-specific register programming. Event presence intentionally checks both dwords for all-ones to tolerate DMA write ordering. TX push logic clears `empty_read_count` and pushes only a single descriptor to a queue the completion path saw empty.

State and dependencies: it reads and mutates queue counters such as `empty_read_count`, uses channel eventq buffers, and dispatches through `efx->type`. Dependencies include `net_driver.h`, `efx_common.h`, `mcdi.h`, and `ptp.h`.

Risks and tests: risks are mostly subtle fast-path assumptions around DMA ordering, queue counter wrap, and false negatives in emptiness checks. Test signals include RX/TX datapath stress, event queue processing, TX push latency tests, stats monotonicity, interrupt selftests, and compile coverage for each NIC type operation table.
