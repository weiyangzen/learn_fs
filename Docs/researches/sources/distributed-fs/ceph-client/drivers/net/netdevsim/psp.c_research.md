# sources/distributed-fs/ceph-client/drivers/net/netdevsim/psp.c

Purpose: simulates PSP device support for netdevsim, including association registration, fake encapsulation/receive handling, stats, and debugfs re-registration.

Important APIs/types/functions: `nsim_psp_init()` creates a `psp_dev` and debugfs `psp_rereg`; `nsim_do_psp()` handles transmit-side PSP encapsulation and simulated peer receive; `nsim_psp_handle_ext()` restores PSP skb extensions after forwarding; `nsim_psp_uninit()` unregisters the PSP device. `nsim_psp_ops` implements config, SPI allocation, key add/delete, key rotate, and stats.

Control flow: transmit retrieves an skb PSP association, verifies it belongs to the sending netdevsim, encapsulates the packet, then either simulates peer PSP receive and marks the skb decrypted or leaves UDP/PSP headers in place with a repaired UDP checksum. SPI allocation increments per-device SPI state and encodes generation into the returned key. Association add stores driver private data and increments a counter; delete clears it. Debugfs reregister unregisters and creates a new PSP device under a mutex.

State and persistence: `netdevsim.psp` stores RCU PSP device pointer, stats with `u64_stats_sync`, debugfs dentry, re-registration mutex, SPI counter, and association count. It is volatile.

Dependencies and integration: depends on `CONFIG_INET_PSP`, PSP core APIs, skb extensions, checksum helpers, RCU, debugfs, and netdevsim forwarding in `netdev.c`.

Risks: driver-private association pointer checks are central to preventing another simulated device from using the key. Stats updates happen in the transmit path and must use sync protection. Re-registration must avoid UAF by clearing the RCU pointer, synchronizing, and unregistering.

Test signals: configure PSP associations, transmit to peers with/without PSP capability, verify decapsulation and UDP checksum fallback, read PSP stats, exercise `psp_rereg`, and ensure association leak warnings fire during uninit.
