# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_nflog.c

## Purpose
Implements the legacy ebtables `nflog` watcher/target, sending bridge packets to the netfilter logging API with NFLOG/ULOG-style group, length, threshold, and prefix parameters.

## Important APIs, Types, And Functions
Important functions are `ebt_nflog_tg`, `ebt_nflog_tg_check`, and `xt_target ebt_nflog_tg_reg`, using `struct ebt_nflog_info`.

## Control Flow
Validation rejects unknown flags and NUL-terminates the prefix. Runtime fills `nf_loginfo` with ULOG parameters, calls `nf_log_packet` for `PF_BRIDGE`, and returns `EBT_CONTINUE` so logging is side-effect-only.

## State And Persistence Behavior
No mutable module state exists. Side effects are logging messages passed to configured netfilter log backends.

## Dependencies And Integration Points
Depends on `nf_log`, bridge ebtables NFLOG UAPI, and xtables target registration. Backend behavior depends on configured nfnetlink log or other logging providers.

## Risks And Test Signals
Risks include invalid flag acceptance, prefix termination, and backend availability. Tests should verify log emission to the right group, length/threshold handling, prefix truncation, and unknown flag rejection.
