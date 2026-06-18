<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_probe.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_probe.c

## Purpose
Probes VL servers and their addresses to discover reachability, preferred endpoint, RTT, and whether the service is YFS-capable.

## Important APIs, Types, And Functions
Exports `afs_vlserver_probe_result()`, `afs_send_vl_probes()`, and `afs_wait_for_vl_probes()`. Internal helpers finish probe rounds, decrement outstanding probe counts, and issue `VL.GetCapabilities` calls to each unprobed address.

## Control Flow
`afs_send_vl_probes()` skips already probed servers and serializes new probe rounds with `AFS_VLSERVER_FL_PROBING`. Each round snapshots the address list, initializes probe state, probes addresses in address-preference order, and accumulates errors. Completion marks address response/failure bits, updates YFS/not-YFS flags and service ID, records best RTT/preferred address, and wakes waiters. `afs_wait_for_vl_probes()` sleeps until any untried server responds or all probing stops.

## State And Persistence
Mutates `vlserver->probe`, `rtt`, flags (`PROBED`, `PROBING`, `RESPONDING`, `IS_YFS`), address-list `responded`, `probe_failed`, and `preferred`, plus VL list preferred server. All state is memory-only.

## Dependencies And Integration Points
Uses VL capability RPC construction in `vlclient.c`, RxRPC peer RTT, address preference priorities, error prioritisation, wait queues, and VL rotation.

## Risks And Edge Cases
All-address local failures, key errors, and network failures must wake waiters and clear probing. Mixed YFS/non-YFS responses must settle service ID carefully. Wait allocation can fail with `-ENOMEM`; signal interruption returns `-ERESTARTSYS` only if no responder was found.

## Test Signals
Reachable/unreachable VL servers, mixed IPv4/IPv6 address preferences, YFS upgrade detection, remote aborts, key expiration, all probes failing, signal interruption while waiting, and preferred RTT selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_probe.c -->
