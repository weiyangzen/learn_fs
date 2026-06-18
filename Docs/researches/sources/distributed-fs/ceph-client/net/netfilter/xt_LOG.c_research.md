# sources/distributed-fs/ceph-client/net/netfilter/xt_LOG.c

Purpose: `LOG` target logs IPv4/IPv6 packets through nf_log and continues traversal.

Important APIs/types/functions: `log_tg()`, `log_tg_check()`, `log_tg_destroy()`, `nf_logger_find_get()`, and `nf_log_packet()`.

Control flow: check validates family, log level, prefix termination, and logger availability, autoloading `nf_log_syslog` for non-nft compat callers. Runtime fills `nf_loginfo`, passes hook/device context and prefix to nf_log, and continues.

State and persistence: per-rule nf_logger reference. Dependencies include x_tables, nf_log, syslog logger, module autoload, and nft compatibility behavior. Risks: missing logger rejects rule, high log volume, prefix termination, and different autoload behavior under nft compat. Test signals: invalid level/prefix, logger autoload, IPv4/IPv6 emission, destroy logger put, and continuation.
