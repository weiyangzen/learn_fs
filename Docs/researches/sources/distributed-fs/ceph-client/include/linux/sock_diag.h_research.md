<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sock_diag.h -->
# sources/distributed-fs/ceph-client/include/linux/sock_diag.h

Purpose: This header declares the in-kernel socket diagnostics registration and helper API used by protocol families to expose socket state over netlink diagnostic interfaces.

Important APIs/types/functions: `struct sock_diag_handler` binds a module owner, address family, and callbacks for dump, per-socket info, and destroy requests. `sock_diag_register()` and `sock_diag_unregister()` manage handler lifetime. `struct sock_diag_inet_compat` provides compatibility dispatch for INET. Cookie helpers include `sock_gen_cookie()`, `sock_diag_check_cookie()`, and `sock_diag_save_cookie()`. Reporting helpers populate memory and filter attributes.

Control flow: Protocol diagnostic code registers a handler; netlink requests call the handler's dump/get/destroy callback. `sock_gen_cookie()` disables preemption around `__sock_gen_cookie()` to keep per-socket cookie generation stable. Destroy notifications route through `sock_diag_destroy_group()` and `sock_diag_has_destroy_listeners()` before broadcasting.

State and persistence: Handler state is held by the diagnostics core; socket cookies persist on socket objects. Net namespace state matters because listener checks read `sock_net(sk)->diag_nlsk`.

Dependencies/integration: Depends on netlink, net namespaces, `struct sock`, `sk_buff`, user namespaces, and UAPI sock_diag definitions. It integrates with AF_INET/AF_INET6 TCP/UDP destroy multicast groups and deliberately ignores raw sockets for destroy broadcast routing.

Risks and test signals: Risks include module lifetime mismatches, incorrect family/protocol-to-group mapping, privacy exposure through filter/memory info, and cookie mismatch handling. Test with `ss`, `inet_diag`, netns-specific listeners, socket destroy events, raw socket exclusion, and module unload after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sock_diag.h -->
