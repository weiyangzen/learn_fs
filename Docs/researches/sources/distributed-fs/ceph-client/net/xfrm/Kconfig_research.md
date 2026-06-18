# sources/distributed-fs/ceph-client/net/xfrm/Kconfig

Purpose: This Kconfig fragment defines the selectable build surface for the XFRM/IPsec subsystem. It establishes the hidden core `XFRM` symbol, the crypto algorithm helper `XFRM_ALGO`, user ABIs (`XFRM_USER`, `XFRM_USER_COMPAT`, `NET_KEY`), optional policy/state features, protocol helpers (`XFRM_AH`, `XFRM_ESP`, `XFRM_IPCOMP`), virtual interfaces, IP-TFS, and ESP-in-TCP.

Important symbols and dependencies: `XFRM` depends on `INET` and selects `GRO_CELLS` and `SKB_EXTENSIONS`, which matches `xfrm_input.c` use of GRO cells and secpath skb extensions. `XFRM_ALGO` selects crypto AEAD/hash/skcipher support used by `xfrm_algo.c`. `XFRM_USER_COMPAT` depends on 64-bit alignment compatibility and unaligned access because `xfrm_compat.c` translates 32-bit netlink layouts. `XFRM_INTERFACE` depends on `XFRM && IPV6` and builds the `xfrm_interface` module. `XFRM_IPTFS` is a tristate RFC 9347 mode. `XFRM_ESPINTCP` is hidden and selected by IPv4/IPv6 ESP Kconfig entries elsewhere.

Control flow and integration: Kconfig selection drives `net/xfrm/Makefile`, which either links core objects into built-in networking or emits feature modules. The options also select crypto algorithms that userspace key managers expect to be present for mandatory IPsec profiles.

State and persistence: No runtime state is stored here. The persistent effect is the configured kernel build graph and module availability.

Risks: Dependency mistakes can produce build configurations where netlink exposes features whose objects are absent, or where protocol code is built without required crypto. Hidden `XFRM_ESPINTCP` relies on selectors outside this file, so regressions can appear only in IPv4/IPv6 ESP builds.

Test signals: Build matrix coverage should include `XFRM=y/m`, `XFRM_USER_COMPAT`, `XFRM_INTERFACE=m/y` with BTF on and off, `XFRM_IPCOMP`, `XFRM_IPTFS`, and ESP-in-TCP selection through IPv4 and IPv6 ESP. Runtime smoke tests should verify `ip xfrm`, PF_KEY legacy behavior if enabled, xfrm interfaces, IPComp SAs, and IP-TFS netlink attributes.
