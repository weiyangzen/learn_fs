# sources/distributed-fs/ceph-client/include/trace/misc/nfs.h

Purpose: Provides NFS/NFSv4 trace formatting helpers for protocol status codes, stability modes, verifiers, pNFS layout I/O modes, recallable-object masks, sequence status flags, and callback operations.

Important APIs/types/functions: Registers many `NFSERR_*`, `NFS4ERR_*`, `NFS_*`, `IOMODE_*`, and callback op enums with `TRACE_DEFINE_ENUM`; exports macros `show_nfs_status`, `show_nfs_stable_how`, `show_nfs4_status`, `show_nfs4_verifier`, `show_pnfs_layout_iomode`, `show_rca_mask`, `show_nfs4_seq4_status`, and `show_nfs4_cb_op`.

Control flow: NFS tracepoint headers include this file and call the helpers from `TP_printk`. The file has macro-generation flow only.

State/persistence: No client/server state is stored. It controls symbolic rendering of values already captured by NFS trace events.

Dependencies/integration: Includes Linux and UAPI NFS headers; integrated with NFS client/server and SUNRPC trace events.

Risks: NFS protocol status coverage must track protocol headers. Missing enum registration degrades trace readability and BPF/perf enum decoding.

Test signals: Build NFS trace events and run NFSv3/v4 client/server tests with trace enabled, checking status and callback strings.
