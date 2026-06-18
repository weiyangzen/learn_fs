# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-global.h

Purpose: defines DPAA2 dequeue result and congestion notification formats plus helpers for parsing queue manager responses.

Important APIs and types: `struct dpaa2_dq` overlays common, frame dequeue, and state-change notification layouts. Status flags report empty, held-active, force-eligible, valid frame, ODP-valid, volatile dequeue, and expired completion. Helpers parse flags, pull/static dequeue identity, pull completion, sequence number, ODP id, FQID, byte/frame counts, frame queue context, embedded `struct dpaa2_fd`, and congestion state in CSCNs. Constants define CSCN size/alignment and congestion bit.

Control flow: DPIO store/poll code obtains dequeue entries, checks flags for valid frames and pull completion, extracts queue metadata and FD, and handles congestion state notifications.

State and persistence: dequeue results are transient hardware response records. Queue counters and congestion state live in QMan/DPIO hardware.

Dependencies and integration points: includes DPAA2 FD definitions, types, and cpumask headers. Used by DPIO services and DPAA2 Ethernet/accelerator consumers.

Risks and test signals: risks include reading invalid fields without required status bits, FQID/frame-count mask mistakes, embedded FD alignment assumptions, and stale congestion notifications. Test pull and static dequeue, empty versus valid entries, expired pull completion, congestion entry/exit, and FD extraction.
