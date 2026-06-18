# sources/distributed-fs/ceph-client/include/net/netfilter/nf_log.h

Purpose: Provides the internal netfilter logging backend registry and packet logging interface used by LOG, ULOG/NFLOG, nft trace, and protocol-family-specific logger modules.

Important APIs/types/functions: `nf_loginfo` describes LOG or ULOG parameters; `nf_logfn` is the backend callback signature; `nf_logger` names a logger, type, module owner, and callback. APIs include `nf_log_register/unregister`, `nf_log_is_registered`, `nf_log_set/unset`, `nf_log_bind_pf/unbind_pf`, `nf_logger_find_get/put`, `nf_log_packet`, `nf_log_trace`, and buffered formatting helpers `nf_log_buf_open/add/close`.

Control flow: Backend modules register loggers by protocol family and type. Rules or tracing code call `nf_log_packet`/`nf_log_trace`; the core chooses the per-net/per-family logger and invokes `logfn` with skb, hook, devices, loginfo, and prefix.

State and persistence: Logger bindings are runtime kernel/module state, partly per-net and partly global. `sysctl_nf_log_all_netns` controls LOG target allowance in all namespaces. Module refcounts protect active loggers.

Dependencies/integration: Depends on netfilter core, skbuff/device context, module ownership, sysctl, and uapi `nf_log.h`; integrates with iptables/nftables logging targets and trace notifications.

Risks/test signals: Check module ref leaks, missing logger fallback, format string paths, per-net binding isolation, and behavior when loggers unregister during packet processing. Test LOG/NFLOG for IPv4, IPv6, bridge, namespace isolation, trace output, and `NF_LOG_F_COPY_LEN` handling.
