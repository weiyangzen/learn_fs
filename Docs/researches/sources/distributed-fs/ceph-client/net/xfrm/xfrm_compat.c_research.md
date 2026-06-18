# sources/distributed-fs/ceph-client/net/xfrm/xfrm_compat.c

Purpose: `xfrm_compat.c` provides the 32-bit compatibility layer for XFRM netlink messages on 64-bit kernels. It translates request and response layouts where native structures include different padding/alignment around 64-bit lifetime fields.

Important APIs and types: The file defines compat variants for lifetime, policy, SA, acquire, SPI, expire, and policy-expire structures. `compat_msg_min[]` mirrors `xfrm_msg_min[]` with 32-bit layout lengths. `compat_policy[]` validates XFRM attributes for compat input. The module registers a `struct xfrm_translator` with `alloc_compat`, `rcv_msg_compat`, and `xlate_user_policy_sockptr`.

Control flow: Kernel-to-userspace translation uses `xfrm_alloc_compat()` to attach a translated skb frag_list and `xfrm_xlate64()` to create a compat netlink message. Attribute translation copies most attributes, uses `nla_put_64bit()` for u64-aligned values, and explicitly includes newer NAT keepalive and IP-TFS attributes. Userspace-to-kernel translation parses compat attributes, computes native length with `xfrm_user_rcv_calculate_len64()`, allocates a native message when needed, copies fixed headers with message-specific padding rules, and expands `XFRMA_SA`/`XFRMA_POLICY` attributes.

State and persistence: The module only registers/unregisters a global translator. Translated messages are temporary allocations. No XFRM policy or SA state is persisted here.

Dependencies and integration: It depends on `xfrm_user.c` policies and message sizes, the translator registry in `xfrm_state.c`, netlink attribute validation, nospec array indexing, and compat socket policy handling through `xlate_user_policy_sockptr`.

Risks: This is ABI-sensitive code. Missing a new XFRM attribute in `xfrm_xlate64_attr()` or `compat_policy[]` can break 32-bit userspace. Wrong padding can corrupt SA lifetime, policy, or expire messages. The `BUILD_BUG_ON(XFRMA_MAX != XFRMA_IPTFS_PKT_SIZE)` guards force updates when UAPI attributes grow.

Test signals: Run 32-bit `ip xfrm`/netlink tests on a 64-bit kernel for SA/policy add, update, dump, expire, acquire, NAT keepalive interval, and all IP-TFS attributes. Include malformed attribute lengths and dump requests that should bypass translation.
