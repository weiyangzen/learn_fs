# sources/distributed-fs/ceph-client/security/smack/smack_netfilter.c

## Purpose

`smack_netfilter.c` is the small Smack netfilter integration layer. Its job is to tag locally generated IPv4, and optionally IPv6, packets with the Smack secid stored in the sending socket's outbound label so downstream networking and peer-security code can use `skb->secmark`.

## Important APIs, types, and functions

The main hook is `smack_ip_output()`, registered in `smack_nf_ops[]` for `NF_INET_LOCAL_OUT`. It uses `skb_to_full_sk()` to find the originating socket, `smack_sock()` to access the socket's `socket_smack` blob, and writes `ssp->smk_out->smk_secid` into `skb->secmark`. `smack_nf_register()` and `smack_nf_unregister()` install or remove the hook array per network namespace using `nf_register_net_hooks()` and `nf_unregister_net_hooks()`. `smack_net_ops` wires those into the pernet subsystem, and `smack_nf_ip_init()` conditionally registers the subsystem after Smack has been enabled.

## Control flow

During Smack device init, `smack_initcall()` calls `smack_nf_ip_init()`. If `smack_enabled` is still zero, the function is a no-op. Otherwise it logs that netfilter hooks are being registered and calls `register_pernet_subsys()`. For every network namespace, `smack_nf_register()` installs the output hooks. At packet transmit time, netfilter invokes `smack_ip_output()` before other security hooks at the SELinux-first priority value; if a full socket is available, the hook copies the Smack outbound secid to `skb->secmark`, then always returns `NF_ACCEPT`.

## State and persistence behavior

This file does not own persistent policy state. It derives all labels from the socket security blob initialized and maintained by `smack_lsm.c`. Its only per-packet state mutation is assigning `skb->secmark`. Hook registration is per network namespace and is undone when namespaces exit through `smack_nf_unregister()`.

## Dependencies and integration points

It depends on netfilter IPv4/IPv6 hook APIs, per-network-namespace registration, socket extraction from `sk_buff`, and Smack socket blobs from `smack.h`. It integrates with the receive-side logic in `smack_lsm.c`, where `smack_from_skb()` prefers `skb->secmark` over NetLabel/CIPSO labels when `CONFIG_NETWORK_SECMARK` is enabled. IPv6 registration exists only when `CONFIG_IPV6` is enabled.

## Risks and test signals

The main risks are missing full socket association for some local packets, secmark overwrites interacting with other netfilter users, namespace registration failures, and configuration skew between `CONFIG_SECURITY_SMACK_NETFILTER`, `CONFIG_NETWORK_SECMARK`, and IPv6 support. Useful tests verify that local IPv4 and IPv6 sends carry the expected secmark, unlabeled or socketless packets are accepted unchanged, per-netns registration/unregistration succeeds, and receive-side policy observes the secmark before falling back to NetLabel.
