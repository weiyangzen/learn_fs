# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/ess.c

## Purpose
`ess.c` implements End Station Support for FDDI Synchronous Bandwidth Allocation RAF frames when `ESS` and non-`SLIM_SMT` are enabled. It receives allocation/change/report RAF frames, updates local synchronous bandwidth MIB state, sends RAF replies or requests, and reconfigures FORMAC TSYNC/FIFO layout.

## Important APIs, Types, And Functions
Public functions are `ess_raf_received_pack()`, `ess_timer_poll()`, and `ess_para_change()`. Internal helpers are `process_bw_alloc()`, `ess_send_response()`, `ess_send_alc_req()`, `ess_send_frame()`, and `ess_config_fifo()`. Static parameter lists validate required RAF parameters for allocation responses and change requests.

## Control Flow
Incoming RAF processing first checks resource type (`SMT_P0015`) and command (`SMT_P0016`). Allocation requests are processed only when local and no static ESS payload is configured; the frame is either returned to local SBA or copied and sent to the network. Allocation replies must pass `smt_check_para()`, primary-ring/resource/reason/TID checks, then `P320F`/`P3210` payload and overhead are applied through `process_bw_alloc()`. Change requests are accepted only as requests with valid path/resource parameters, then replied to if bandwidth update succeeds. Report requests return the current allocation.

`process_bw_alloc()` bounds payload and overhead, computes bytes per `T_NEG` (`sync_bw`), updates PATH SBA MIBs, configures FIFO, and writes FORMAC TSYNC. `ess_timer_poll()` periodically sends allocation requests until desired ESS static values match current path allocation.

## State And Persistence
ESS state is in `smc->ess` (`sync_bw_available`, `sync_bw`, `alloc_trans_id`, timer poll flags, pending local reply) and MIB fields (`fddiESSPayload`, `fddiESSOverhead`, `fddiPATHSbaPayload`, `fddiPATHSbaOverhead`). There is no disk persistence. Hardware-visible persistence is transient FORMAC TSYNC and FIFO split configuration.

## Dependencies And Integration Points
The file depends on SMT frame construction/parsing, `smt_p.h` RAF parameter IDs, `sba.h`/`sba_def.h` constants, `smt_send_frame()`, `smt_build_frame()`, `smt_get_mbuf()`, `smt_free_mbuf()`, FORMAC TSYNC/FIFO functions, MIB state, and optional local SBA handoff through `sba_reply_pend`.

## Risks And Edge Cases
Some parameter pointers in the change path are used after `smt_check_para()` without individual null checks. The allocation-request address validation checks only five of six address bytes. The bandwidth equation uses signed arithmetic and can produce negative TSYNC values intentionally; overflow or unit mistakes affect synchronous service. Reinitializing TX FIFO while traffic is active depends on `formac_reinit_tx()` being safe.

## Test Signals
Test malformed RAF frames, missing parameters, non-primary path, wrong resource type, wrong transaction ID, success and denied reason codes, payload zero deallocation, payload/overhead bounds, timer-driven allocation requests, local SBA pending reply handling, network reply sending, TSYNC register update, FIFO reinit when sync bandwidth first appears, and static ESS target convergence.
