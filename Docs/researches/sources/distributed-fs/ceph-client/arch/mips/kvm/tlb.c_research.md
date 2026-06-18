## sources/distributed-fs/ceph-client/arch/mips/kvm/tlb.c

Purpose: Implements MIPS KVM VZ TLB helpers that must run from host kernel address space: root TLB invalidation, guest TLB lookup, local guest/root flushes, guest TLB save/load, and Loongson-specific invalidations.

Important APIs, types, and functions: Exported globals are `GUESTID_MASK`, `GUESTID_FIRST_VERSION`, and `GUESTID_VERSION_MASK`. Public helpers include `kvm_vz_host_tlb_inv()`, `kvm_vz_guest_tlb_lookup()`, `kvm_vz_local_flush_roottlb_all_guests()`, `kvm_vz_local_flush_guesttlb_all()`, `kvm_vz_save_guesttlb()`, `kvm_vz_load_guesttlb()`, and optional Loongson clear functions. Internal helpers manage root ASID and GuestCtl1.RID.

Control flow: Host TLB invalidation disables interrupts and HTW, sets root GuestID to the active guest ID when supported, probes a root TLB entry by VPN2 plus root ASID, invalidates it if found, restores EntryHi/RID/HTW, and flushes VTag I-cache if necessary. Guest TLB lookup probes guest TLB registers, reads matching EntryLo/PageMask, restores clobbered guest registers, validates the selected EntryLo, and computes GPA. Flush functions iterate root or guest TLB entries, replacing them with unique invalid entries. Save/load functions preserve guest TLB CP0 registers, set the appropriate root GuestID, then read or write indexed guest TLB entries.

State and persistence: Operates on hardware TLB and GuestCtl registers, preserving original CP0 state around operations. Save/load serializes entries into caller-provided `struct kvm_mips_tlb` buffers. GuestID globals are exported for VZ backend coordination.

Dependencies and integration points: Depends on CP0/TLB hazard helpers, HTW controls, CPU type data, GuestID/VZ registers, MIPS ASID context, and Loongson diagnostic registers. Called by MMU fault handling, VZ backend code, and remote flush paths.

Risks: These functions are highly sensitive to interrupt disabling, HTW state, hazard barriers, and CP0 register restoration. `BUG_ON(idx >= tlbsize)` can panic on unexpected probe state. Guest TLB lookup explicitly does not handle MIPS32 XPA PFN splitting. Root GuestID must be cleared or host root TLB operations can target guest entries accidentally.

Test signals: Root TLB invalidation with and without GuestID, guest TLB lookup hit/miss/invalid-entry cases, full root and guest flushes, Octeon3 machine-check inhibit path, save/load ranges with foreign GuestID entries, Loongson VTLB/FTLB invalidation, and HTW restart after exceptions.
