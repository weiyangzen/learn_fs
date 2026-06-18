<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h

Purpose: Defines the shared in-kernel data model and helper API for Book3S KVM XIVE support, covering both XICS-on-XIVE compatibility and native XIVE device mode.

Important APIs/types/functions: Provides `struct kvmppc_xive_irq_state`, `struct kvmppc_xive_src_block`, `struct kvmppc_xive_ops`, `struct kvmppc_xive`, and `struct kvmppc_xive_vcpu`; constants `KVMPPC_XIVE_FIRST_IRQ`, `KVMPPC_XIVE_NR_IRQS`, `KVMPPC_XIVE_Q_COUNT`, and feature flags; helpers `kvmppc_xive_select_irq()`, `kvmppc_xive_find_server()`, `kvmppc_xive_find_source()`, `kvmppc_xive_vp()`, `kvmppc_xive_vp_in_use()`, `xive_prio_from_guest()`, `xive_prio_to_guest()`, `__xive_read_eq()`, and common function declarations used by both implementations.

Control flow: The header itself has inline lookup and decoding logic. Source lookup splits guest IRQs into ICS-like blocks and per-block source indexes. VP lookup packs a guest vCPU/server number into a hardware VP inside the VM VP block. Queue reads advance index/toggle state only when a valid entry is observed. Priority mapping clamps guest priorities above 5 to host priority 6 while preserving `0xff` masked state.

State and persistence: The structures describe all long-lived XIVE VM state: source validity, emulated IPI or pass-through backing IRQ, guest and actual target, PQ snapshots, LSI assertion, migration flags, native EISN, VP identifiers, queue pages, escalation IRQs, pending ICP state, queue provisioning bitmap, mapping inode, locks, and delayed restore counters.

Dependencies and integration points: Gated by `CONFIG_KVM_XICS` and includes `book3s_xics.h`. It integrates with `book3s_xive.c`, `book3s_xive_native.c`, Book3S KVM architecture state, Linux XIVE structs, KVM device ioctls, and guest entry code that consumes `xive_cam_word` and saved TIMA state.

Risks: Field semantics are shared across two modes, so changes can break XICS compatibility or native XIVE differently. `kvmppc_xive_find_server()` is a linear vCPU scan and assumes stable vCPU attachment under caller serialization. `__xive_read_eq()` depends on XIVE queue toggle format and correct big-endian entry reads.

Test signals: Compile coverage for `CONFIG_KVM_XICS`, XICS-on-XIVE and native-XIVE runtime tests, vCPU hotplug, queue wraparound tests, migration state tests, and pass-through IRQ mapping tests are the main signals.

Source read size: 313 lines, 8417 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h -->
