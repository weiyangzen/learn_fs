<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h

## Purpose
This header defines the SCSI RDMA Protocol transport class for SRP remote ports, reconnection/fail-fast/dev-loss timers, and initiator-driver callbacks.

## Important APIs, Types, And Functions
It defines SRP rport roles, `struct srp_rport_identifiers`, `enum srp_rport_state`, `struct srp_rport`, and `struct srp_function_template`. APIs attach/release the transport, get/put/add/delete rports, validate and parse timeout values, reconnect rports, start/stop transport-layer fail timers, remove hosts, handle command timeout with `srp_timed_out()`, and gate I/O with `srp_chkready()`.

## Control Flow
Drivers add SRP rports to a host. In normal state, I/O proceeds. When connectivity is disrupted, reconnect work and fast-I/O-fail/dev-loss delayed work transition rports through blocked, fail-fast, and lost states. `srp_chkready()` maps those states to SCSI result codes for queuecommand paths.

## State And Persistence
`struct srp_rport` stores device identity, 16-byte port ID, role, LLDD private data, mutex-protected state, reconnect delay/counter, and delayed work for reconnect, fast fail, and dev loss. State is runtime and sysfs-visible depending on template flags.

## Dependencies And Integration Points
It depends on transport class, Linux types, mutexes, SCSI host/status/command concepts, and SRP initiator LLDDs. It parallels FC remote-port ready checking but for RDMA/SRP transports.

## Risks
Timer validation must prevent nonsensical reconnect/fast-fail/dev-loss ordering. `srp_chkready()` deliberately allows blocked I/O unless fail-fast/lost, so timeout policy is critical. Reconnect callbacks must coordinate with outstanding I/O termination and rport deletion.

## Test Signals
Validate rport add/delete/refcounting, timeout parsing and validation, reconnect work scheduling, fast-fail/dev-loss transitions, `srp_chkready()` state matrix, `srp_timed_out()` behavior with `reset_timer_if_blocked`, and host removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_transport_srp.h -->
