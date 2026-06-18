
# sources/distributed-fs/ceph-client/net/netfilter/nf_log.c

Purpose: Implements the generic netfilter logger registry, per-net logger selection, proc/sysctl controls, and shared bounded log-buffer helpers used by concrete logger modules.

Important APIs and functions: Registry operations are `nf_log_register()`, `nf_log_unregister()`, `nf_log_is_registered()`, `nf_logger_find_get()`, and `nf_logger_put()`. Per-net selection uses `nf_log_set()`, `nf_log_unset()`, `nf_log_bind_pf()`, and `nf_log_unbind_pf()`. Packet emission goes through `nf_log_packet()` or `nf_log_trace()`. Buffer helpers are `nf_log_buf_open()`, `nf_log_buf_add()`, and `nf_log_buf_close()`. `netfilter_log_init()` registers per-net proc/sysctl setup.

Control flow: Logger providers register a `struct nf_logger` per protocol family/type. Packet logging selects either an explicit logger type from `loginfo` or the per-net bound logger, formats the prefix, and calls the provider callback under RCU. Procfs iterates per-family logger bindings. Sysctl write accepts a logger name or `NONE` and updates the per-net RCU pointer.

State and persistence: Global state is `loggers[NFPROTO_NUMPROTO][NF_LOG_TYPE_MAX]`, protected by `nf_log_mutex` and read under RCU, plus `sysctl_nf_log_all_netns`. Per-net state lives in `net->nf.nf_loggers[]` and sysctl/proc headers. The emergency log buffer is a singleton fallback when allocation fails.

Dependencies and integration: Concrete loggers such as `nf_log_syslog.c` register here. nftables/iptables logging targets call `nf_log_packet()` or module-get helpers. Per-net lifecycle uses procfs and sysctl infrastructure.

Risks: Risks include RCU pointer lifetime, module refcount races, emergency buffer use with bottom halves disabled, sysctl table duplication/free for non-init netns, prefix truncation, and global `nf_log_all_netns` exposure. Tests should cover logger registration conflicts, namespace-specific binding, module unload while logging, proc/sysctl read/write, allocation failure fallback, and trace logging without explicit `loginfo`.
