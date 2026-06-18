# sources/distributed-fs/ceph-client/include/trace/events/ceph.h

## Purpose
`ceph.h` defines CephFS client tracepoints for MDS request lifecycle and capability message handling.

## Important APIs, types, and functions
It defines `enum ceph_mdsc_suspend_reason` with symbolic mappings for no map, no active MDS, rejected, and session suspension. Events are `ceph_mdsc_submit_request`, `ceph_mdsc_suspend_request`, `ceph_mdsc_resume_request`, `ceph_mdsc_send_request`, `ceph_mdsc_complete_request`, and `ceph_handle_caps`.

## Control flow
MDS request events follow submit, suspend, resume, send, and completion. Submit derives inode identity from `req->r_inode` or `req->r_dentry`; suspend records the target MDS when a session is present; complete calculates latency from request start/end timestamps. Capability handling records MDS, cap op, vino, and sequence fields.

## State and persistence behavior
The header owns no state. Records snapshot request tid, operation id/name, inode number and snap id, MDS rank, error, latency, capability vino, and seq/mseq/issue_seq.

## Dependencies and integration points
It depends on CephFS internal MDS request/session/client/inode/cap structures and helpers such as `ceph_mds_op_name()`, `ceph_cap_op_name()`, `ceph_ino()`, and `ceph_snap()`. It integrates CephFS with ftrace/perf/BPF diagnostics.

## Risks and test signals
Risks include incomplete inode identification when neither inode nor dentry is available, latency underflow if timestamps are not ordered, and suspend reason enum drift. Test signals are MDS operation workloads showing submit/send/complete sequences, forced session/map suspension, error completions, and cap messages with expected sequence numbers.
