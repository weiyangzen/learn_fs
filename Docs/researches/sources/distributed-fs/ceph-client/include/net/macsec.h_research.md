<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/macsec.h -->
# sources/distributed-fs/ceph-client/include/net/macsec.h

## Purpose
`macsec.h` defines the MACsec Security Entity data model and offload callback ABI shared by the software MACsec driver, PHY offload providers, and MAC offload-capable netdevices.

## Important APIs, types, and functions
Important types are `sci_t`, `ssci_t`, `salt_t`, `pn_t`, `struct macsec_key`, RX/TX SC and SA structures, per-CPU stats structures, `struct macsec_secy`, `struct macsec_context`, and `struct macsec_ops`. Helper APIs include `macsec_pn_wrapped`, `macsec_send_sci`, `macsec_get_real_dev`, `macsec_netdev_is_offloaded`, `macsec_netdev_priv`, and `sci_to_cpu`.

## Control flow
MACsec control paths populate a `macsec_context` for device open/stop, SecY add/update/delete, RXSC/RXSA/TXSA updates, stats reads, and optional tag insertion. Packet-number state lives under SA spinlocks; SC/SA pointers are RCU-managed. Offload implementers use the same context union for MAC and PHY offload and return statistics through the union of stats pointers.

## State and persistence
State is runtime cryptographic and security-association state: keys and salts, next packet numbers, active flags, RCU/refcounted SC/SA lifetimes, per-CPU counters, replay protection settings, validation mode, ICV/key length, and offload metadata dst. No on-disk persistence exists; userspace configuration rebuilds state.

## Dependencies and integration points
It depends on crypto AEAD handles, netdevice/VLAN helpers, workqueue/RCU work, per-CPU u64 stats synchronization, and UAPI MACsec enums. It integrates with hardware drivers through `macsec_ops` exposed on devices or PHYs.

## Risks and test signals
Risks include PN wrap and XPN split-half handling, RCU/refcount teardown of active SAs, VLAN real-device private lookup, stats synchronization, mismatch between offload type and context union member, and SCI-insertion policy. Tests should exercise PN wrap callbacks, SA add/update/delete with `update_pn`, VLAN offload devices, RX/TX stats reads, `send_sci` policy with multiple RXSCs, and software/offload parity.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/macsec.h` completely for this pass (387 lines, 11011 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/macsec.h -->
