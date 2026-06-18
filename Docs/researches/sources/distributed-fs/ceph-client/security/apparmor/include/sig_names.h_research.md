# sources/distributed-fs/ceph-client/security/apparmor/include/sig_names.h

Purpose: provides architecture-aware signal-number normalization and audit names for AppArmor signal mediation.

Important data: `sig_map[MAXMAPPED_SIG]` maps Linux signal numbers to stable AppArmor internal signal IDs, folding aliases such as `SIGPOLL`/`SIGIO` and optional architecture signals behind `#ifdef`s. `sig_names[MAXMAPPED_SIGNAME]` maps those internal IDs to policy/audit names, with `"exists"` reserved as the final existence-test entry.

Control flow: `ipc.c` includes this file and calls `map_signal_num()` to map `sig` into a DFA input symbol. Audit code then renders `sig_names[ad->signal]` or an `rtmin+N` form for realtime signals.

State and persistence: static read-only tables only.

Dependencies and integration: depends on `<linux/signal.h>` and `include/signal.h`; integrates with `AA_SFS_SIG_MASK`, signal DFA policy, and audit records. Risks are architecture-specific alias drift and table-size mismatch with `MAXMAPPED_SIG`. Test by compiling on architectures with optional `SIGEMT`, `SIGSTKFLT`, `SIGLOST`, and `SIGUNUSED`, and by mediating standard, unknown, zero, and realtime signals.
