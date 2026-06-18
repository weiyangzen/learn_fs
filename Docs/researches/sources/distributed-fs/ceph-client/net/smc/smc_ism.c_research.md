# sources/distributed-fs/ceph-client/net/smc/smc_ism.c

## Purpose
`smc_ism.c` implements SMC-D support over ISM/DIBS devices. It registers as a DIBS client, discovers and orders SMC-D devices, manages VLAN IDs, registers/attaches/detaches DMBs, maps DMB indexes to SMC connections, handles ISM events and interrupts, provides SMC-D netlink device dumps, and signals peer shutdown/testlink events.

## Important APIs, Types, and Functions
Global state includes `smcd_dev_list`, `smc_ism_v2_capable`, and `smc_ism_v2_system_eid`. Public APIs include `smc_ism_cantalk()`, `smc_ism_set_conn()`, `smc_ism_unset_conn()`, `smc_ism_get_vlan()`, `smc_ism_put_vlan()`, `smc_ism_register_dmb()`, `smc_ism_unregister_dmb()`, `smc_ism_support_dmb_nocopy()`, `smc_ism_attach_dmb()`, `smc_ism_detach_dmb()`, `smc_ism_signal_shutdown()`, `smc_ism_get_system_eid()`, `smc_ism_get_chid()`, `smc_ism_is_v2_capable()`, `smc_ism_init()`, `smc_ism_exit()`, and `smcd_nl_get_device()`.

## Control Flow
`smc_ism_init()` resets v2 capability, creates a system EID, and registers `smc_dibs_client`. Device add allocates `struct smcd_dev`, creates a connection pointer table and ordered event workqueue, sets PNET ID, detects v2 capability through loopback or reserved VLAN support, and inserts the device in preference order. DMB registration fills a `dibs_dmb` with peer GID and VLAN, then stores returned token, index, CPU address, DMA address, and length in the buffer descriptor. IRQ handling looks up a connection by DMB number under a spinlock and schedules its RX tasklet. Device and software events are copied from IRQ context into event work, where peer shutdown triggers core link-group termination and testlink requests can be answered.

## State and Persistence
All state is transient: global device list, per-device VLAN refcount list, per-DMB connection table, event workqueue, link-group count, going-away flag, and v2 system EID. VLAN IDs are refcounted and added to hardware only for the first user, then removed on the last put.

## Dependencies and Integration Points
The file integrates DIBS/ISM device ops, SMC core termination and buffer descriptors, PNET lookup, generic netlink, PCI metadata helpers, VLAN constants, and SMC-D CDC receive tasklets. Core calls ISM helpers during SMC-D connection creation, buffer creation, no-copy attach, close, and module shutdown.

## Risks
DIBS callbacks can run in interrupt context, so allocation, queueing, and connection table access must remain IRQ-safe. VLAN reference handling must match link-group lifetime or hardware VLAN entries can leak or be removed too early. No-copy DMB attach creates a connection-owned "ghost" send buffer that must detach exactly once. Device unregister sets `going_away`, terminates groups, destroys the event queue, and frees connection arrays, so queued work must be drained by workqueue destruction.

## Test Signals
Test SMC-D connect/close with and without VLANs, DMB registration failure paths, loopback no-copy attach/detach, ISM device add/remove, peer shutdown events, IRQ-driven receive tasklet scheduling, v2 EID reporting, generic netlink SMCD device dumps, and unload while SMC-D groups are active.
