# sources/distributed-fs/ceph-client/net/netfilter/xt_NFLOG.c

Purpose: `NFLOG` target sends packet logs to nfnetlink_log groups and continues traversal.

Important APIs/types/functions: `nflog_tg()`, `nflog_tg_check()`, `nflog_tg_destroy()`, `nf_logger_find_get()`, and `nf_log_packet()`.

Control flow: check validates flags and prefix termination, gets ULOG logger, and autoloads `nfnetlink_log` outside nft compat. Runtime fills ulog copy length/group/threshold/flags and logs the packet.

State and persistence: per-rule logger reference; userspace receives netlink log records. Dependencies include x_tables, nf_log, nfnetlink_log, and module autoload. Risks: logger absence rejects rules, copy length and threshold performance, invalid flags, and nft compat autoload differences. Test signals: flag mask rejection, prefix termination, logger autoload, group delivery, copy-len flag, and destroy put.
