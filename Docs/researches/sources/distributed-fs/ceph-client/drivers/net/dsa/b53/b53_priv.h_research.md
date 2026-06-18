# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_priv.h

Purpose: private B53 core/transport contract: device state, IO ops, ARL ops, chip predicates, locked register wrappers, ARL conversion helpers, and exported common-core prototypes.

Important APIs/types/functions: `struct b53_io_ops`, `struct b53_arl_ops`, `struct b53_device`, `struct b53_port`, `struct b53_vlan`, `struct b53_pcs`, and `struct b53_arl_entry`. Inline `is*()` helpers classify chips. `b53_build_op()` creates mutex-protected `b53_read*()`/`write*()` wrappers.

Control flow: transports implement `b53_io_ops`, allocate/register the core, and common code uses locked wrappers plus chip predicates/ARL ops to program hardware.

State and persistence behavior: defines runtime layout. `struct b53_device` caches chip metadata, ports, VLANs, page selection, ops, and SerDes state for the device lifetime.

Dependencies and integration points: kernel mutex/phylink/etherdevice/DSA headers, `b53_regs.h`, optional BCM47xx reset GPIO helpers, common and transport modules.

Risks: missing ops callbacks cause crashes; chip predicates must stay aligned with chip table; ARL packing is variant-sensitive; `b53_for_each_port()` depends on `enabled_ports`.

Test signals: all-config builds, ARL encode/decode tests, lockdep on register paths, and probe initialization checks.
