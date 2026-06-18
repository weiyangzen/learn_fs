# sources/distributed-fs/ceph-client/net/netfilter/nft_log.c

Purpose: implements the nftables `log` expression for syslog, nfnetlink log, and audit logging of matching packets.

Important APIs/types/functions: `struct nft_log` contains `nf_loginfo` and a prefix pointer. `nft_log_eval()` either calls `nft_log_eval_audit()` for audit level or `nf_log_packet()` for logger backends. `nft_log_modprobe()` requests `nf_log_syslog` or `nfnetlink_log` when logger lookup needs module loading. Init parses prefix, group, snaplen, qthreshold, log level, and flags.

Control flow: init defaults to `NF_LOG_TYPE_LOG`; specifying group switches to ULOG and forbids log flags. Prefix is allocated unless absent, in which case a static empty string is used. Syslog level defaults to warning and must not exceed audit. Non-audit paths acquire a logger with `nf_logger_find_get()` and may return `-EAGAIN` after module request. Eval emits audit records with skb mark and nf skb data, or calls logger backend with hook/device context. Destroy frees dynamic prefix and drops logger references except audit.

State/persistence: expression state is logging configuration, prefix allocation, and logger reference. Dependencies include audit, nf_log, netlink log, module autoloading, and family-specific logger availability. Risks include prefix ownership mistakes, invalid level/group combinations, logger ref imbalance, audit path bypassing logger refs, and logging from packet context under memory pressure. Test signals: syslog and NFLOG modes, audit mode with audit disabled/enabled, prefix length limits, module autoload, invalid group+level/flags combinations, dump round trip, and unload after logger use.
