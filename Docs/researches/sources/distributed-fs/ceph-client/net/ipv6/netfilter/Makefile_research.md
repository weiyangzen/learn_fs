# sources/distributed-fs/ceph-client/net/ipv6/netfilter/Makefile

Purpose: Maps IPv6 netfilter Kconfig symbols to object files and composite objects.

Important APIs/types/functions: It builds legacy tables (`ip6_tables.o`, `ip6table_filter.o`, mangle/raw/security/nat), defrag composite `nf_defrag_ipv6.o`, socket/tproxy helpers, reject/dup cores, nftables objects, xtables matches (`ip6t_ah.o`, `ip6t_eui64.o`, `ip6t_frag.o`, `ip6t_ipv6header.o`, `ip6t_mh.o`, `ip6t_hbh.o`, `ip6t_rpfilter.o`, `ip6t_rt.o`, `ip6t_srh.o`) and targets (`ip6t_NPT.o`, `ip6t_REJECT.o`, `ip6t_SYNPROXY.o`).

Control flow: Kbuild includes each object through `obj-$(CONFIG_...)`; the comment notes link order matters, placing `ip6_tables.o` before dependent legacy tables.

State and persistence: No runtime state; it persists build graph ordering and module composition.

Dependencies/integration: Tightly coupled to Kconfig symbol names and module autoload aliases from target/match files.

Risks and test signals: Risks are stale symbols, incorrect link order for table users of `ip6t_do_table`, and missing composite members for defrag. Test with modular and built-in configurations, `modprobe ip6table_filter`, and symbol dependency checks.
