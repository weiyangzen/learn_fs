# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funcore/fun_dev.c

## Purpose
Provides shared PCI-function services for Fungible devices: BAR mapping, DMA mask setup, NVMe-like controller enable/disable, admin queue setup, admin command submission, resource helpers, MSI-X allocation/reservation, and deferred service work.

## Important APIs, Types, And Functions
Public exports include `fun_dev_enable()`, `fun_dev_disable()`, `fun_submit_admin_cmd()`, `fun_submit_admin_sync_cmd()`, `fun_get_res_count()`, `fun_res_destroy()`, `fun_bind()`, `fun_reserve_irqs()`, `fun_release_irqs()`, `fun_serv_stop()`, `fun_serv_restart()`, and `fun_serv_sched()`. Internal command state uses `struct fun_cmd_ctx` and `struct fun_sync_cmd_ctx`.

## Control Flow
`fun_dev_enable()` maps BAR0, sets 64-bit DMA masks, enables the PCI memory device, sanitizes controller ready state, records CAP/doorbell geometry, initializes service work, allocates MSI-X, initializes the IRQ bitmap, enables the admin queue, queries queue limits, saves PCI state, and stores driver data. Admin queue setup allocates a `fun_queue`, command contexts, sbitmap tags, IRQ 0, writes AQA/ASQ/ACQ, enables the controller, and optionally creates/posts an RQ. Async submission obtains a tag, fills CID/context, copies the request into the SQ, advances the tail, and rings the SQ doorbell. CQ completion dispatches events or command callbacks and releases tags. Sync submission waits with timeout and suppresses later commands on timeout.

## State And Persistence
State is live PCI/MMIO and memory state in `struct fun_dev`: BAR, doorbells, CAP/CC shadows, admin queue, tag bitmap, command contexts, firmware upgrade handle, IRQ bitmap, service flags, and callbacks. No durable state is written; PCI state is saved for kernel/device recovery.

## Dependencies And Integration Points
Uses PCI/MSI-X, DMA, NVMe register definitions, sbitmap queues, wait/completion APIs, workqueues, and `fun_queue`/`fun_hci` command formats. `funeth` subclasses this via `struct fun_ethdev`.

## Risks
Admin command timeout calls `fun_admin_stop()`, suppressing future commands and requiring higher-level recovery. Callback data uses atomic exchange/cmpxchg to resolve completion races, so callers must keep context valid until abandoned or completed. IRQ reservation trusts callers to release exact indices. Device ready polling depends on NVMe CAP timeout semantics. Cleanup ordering must destroy firmware handles before disabling the admin queue.

## Test Signals
Probe/remove cycles, admin queue interrupt completions, sync command success/failure/timeout, resource count queries, bind/destroy commands, IRQ reserve/release exhaustion, service work scheduling/stop/restart, and fault injection at every enable-stage label.
