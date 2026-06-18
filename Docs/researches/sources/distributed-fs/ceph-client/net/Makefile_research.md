# sources/distributed-fs/ceph-client/net/Makefile

Purpose: top-level networking build manifest. It maps networking Kconfig symbols to directories and object files, establishing which network subsystems are built into `net/` for a particular kernel configuration.

Important APIs, types, and functions: this is Kbuild syntax. Important entries include always-built `devres.o socket.o core/` plus unconditional `ethernet/ 802/ sched/ netlink/ bpf/ ethtool/`, and conditional directories such as `ipv4/`, `ipv6/`, `netfilter/`, `appletalk/`, `atm/`, `9p/`, `ceph/`, `wireless/`, `mac80211/`, `mptcp/`, and `shaper/`. The file uses `obj-y`, `obj-$(CONFIG_...)`, and one `ifneq ($(CONFIG_VLAN_8021Q),)` block.

Control flow: Kbuild recursively descends into directories selected by enabled symbols. `CONFIG_ATALK` controls `appletalk/`, `CONFIG_ATM` controls `atm/`, and `CONFIG_NET_9P` controls `9p/`. LLC is intentionally linked before `net/802/`, documented by a comment.

State and persistence: no runtime state; persistent effect is the build graph derived from `.config`. The order of object and directory lists affects link order for built-in networking code.

Dependencies and integration points: integrates with `net/Kconfig` and each child directory Makefile. It is the build-side counterpart to the top-level networking configuration and governs whether source files in this research set become built-in, modules, or omitted.

Risks: missing or misordered entries can break symbol resolution, init ordering, or protocol registration. The unconditional inclusion of some directories means their internal Makefiles must handle disabled features carefully. Formatting churn can obscure link-order intent.

Test signals: compare enabled `.config` symbols with `make V=1` build traversal, verify `CONFIG_ATALK=y/m`, `CONFIG_ATM=y/m`, and `CONFIG_NET_9P=y/m` pull the expected subdirectories, and build with `CONFIG_VLAN_8021Q` both enabled and disabled.
