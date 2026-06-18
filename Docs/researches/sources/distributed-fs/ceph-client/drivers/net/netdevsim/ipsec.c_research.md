# sources/distributed-fs/ceph-client/drivers/net/netdevsim/ipsec.c

Purpose: implements a simulated XFRM/IPsec hardware offload table for netdevsim and a debugfs reader for installed security associations.

Important APIs/types/functions: `nsim_ipsec_init()` attaches `xfrmdev_ops`, advertises ESP offload features, and creates the debugfs `ipsec` file. `nsim_ipsec_add_sa()` validates and installs SAs, `nsim_ipsec_del_sa()` removes them, and `nsim_ipsec_tx()` validates outbound skb security path state against the simulated table.

Control flow: adding an SA rejects unsupported protocols, compression, and non-crypto offload. It finds a free slot, validates AEAD as RFC4106 AES-GCM with 128-bit auth and a 128-bit key plus optional salt, records direction/address/key material, marks `xso.offload_handle` with `NSIM_IPSEC_VALID`, and increments count. Tx checks secpath, input xfrm state, slot bounds, slot use, and protocol before incrementing a tx counter.

State and persistence: `struct nsim_ipsec` stores up to 33 SAs, a debugfs dentry, install count, and tx count in netdev private memory. State is volatile and should be empty by teardown; teardown logs if SAs remain.

Dependencies and integration: depends on XFRM device offload APIs, crypto AEAD metadata, netdev feature flags, debugfs, and the netdevsim transmit path in `netdev.c`, which calls `nsim_ipsec_tx()` before forwarding.

Risks: delete trusts the offload handle index after masking; malformed or stale handles could report invalid slots. The code simulates metadata validation only; it does not encrypt/decrypt payloads. Key parsing casts key bytes to `u32 *`, so assumptions about key buffer alignment follow kernel XFRM allocation behavior.

Test signals: add inbound/outbound ESP/AH offload states, reject unsupported algorithms/auth sizes/offload types, inspect debugfs output, transmit with missing or invalid secpath, and verify teardown warning when SAs are leaked.
