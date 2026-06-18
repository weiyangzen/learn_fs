# sources/distributed-fs/ceph-client/net/netfilter/xt_AUDIT.c

Purpose: `AUDIT` target emits audit records for accepted/dropped/matching packets and continues traversal.

Important APIs/types/functions: `audit_tg()`, `audit_tg_ebt()`, `audit_tg_check()`, `audit_log_start()`, `audit_log_nf_skb()`, and target registrations for generic and bridge families.

Control flow: runtime skips work when audit is off or allocation fails, logs skb mark and packet fields, ends the audit record, and returns `XT_CONTINUE`; bridge wrapper returns `EBT_CONTINUE`. Checkentry validates audit type range.

State and persistence: no private persistent state; audit subsystem stores records. Dependencies include Linux audit, x_tables, ebtables, skb family helpers, IPv4/IPv6/ARP/bridge aliases. Risks: silent continuation on audit allocation failure, type not used by body beyond validation, and bridge verdict differences. Test signals: audit disabled/enabled, invalid type, bridge path, IPv4/IPv6/ARP aliases, and continued traversal.
