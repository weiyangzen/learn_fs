# sources/distributed-fs/ceph-client/net/xfrm/xfrm_device.c

Purpose: `xfrm_device.c` manages hardware IPsec offload integration. It validates device capabilities, installs SA and policy offload state, prepares skbs for device encryption, resumes packets after async offload, and flushes offloaded state on netdevice events.

Important APIs: Under `CONFIG_XFRM_OFFLOAD`, exported functions include `validate_xmit_xfrm()`, `xfrm_dev_state_add()`, `xfrm_dev_policy_add()`, `xfrm_dev_offload_ok()`, `xfrm_dev_resume()`, and `xfrm_dev_backlog()`. Always-built notifier logic validates `NETIF_F_HW_ESP` feature combinations and flushes state/policy on device down or unregister.

Control flow: `validate_xmit_xfrm()` runs near transmit, skips already-resumed packets, checks packet-offload device affinity, handles GSO segmentation when rerouted or sequence overflow would occur, prepares mode-specific packet pointers, calls `x->type_offload->xmit()`, and queues async results through `xfrm_backlog` when needed. `xfrm_dev_state_add()` validates user offload flags, direction, TFC incompatibility, device lookup, ESN support, and type-offload presence before invoking `xdo_dev_state_add()`. Policy add is restricted to packet offload. `xfrm_dev_offload_ok()` checks MTU/GSO, tunnel header constraints, IPv4 options, IPv6 extension headers, and optional driver callback.

State and persistence: Offload state lives in `x->xso` and policy `xp->xdo`, holding device pointers, trackers, direction, and offload type. Per-CPU softnet `xfrm_backlog` temporarily stores packets requiring resume.

Dependencies and integration: The file depends on netdevice `xfrmdev_ops`, ESP type-offload callbacks, dst/MTU helpers, GSO, XFRM state/policy flushing, and network device notifiers.

Risks: Wrong pointer preparation can make hardware encrypt the wrong bytes. Device mismatch in packet offload must drop, not fall back, to avoid bypassing policy. ESN, GSO sequence overflow, and tunnel-size checks are subtle interoperability and security boundaries. Notifier failures can leave stale hardware state.

Test signals: Test crypto and packet offload devices, reroute to non-offload devices, GSO ESP segmentation, ESN support/no-support, IPv4 options, IPv6 extension headers, tunnel PMTU, device down/unregister flushing, async `-EINPROGRESS` resume, and policy offload direction validation.
