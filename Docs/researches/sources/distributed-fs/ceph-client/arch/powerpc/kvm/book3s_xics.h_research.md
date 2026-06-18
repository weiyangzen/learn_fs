# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.h

Purpose: this header defines the private XICS data model shared by Book3S KVM XICS implementation and real-mode helpers. It gives the interrupt source hierarchy, atomic ICP state layout, per-vCPU presenter object, per-ICS source table, and top-level XICS device structure.

Important APIs and types: `struct ics_irq_state` represents one interrupt source. `union kvmppc_icp_state` packs output, resend, CPPR, MFRR, pending priority, and XISR into one machine word for atomic compare/exchange. `struct kvmppc_icp` is the per-vCPU interrupt presenter, including resend bitmap and real-mode deferred-action fields. `struct kvmppc_ics` is one source block with 1024 IRQ states. `struct kvmppc_xics` is the VM-level device. Inline helpers `kvmppc_xics_find_server()` and `kvmppc_xics_find_ics()` resolve vCPU presenters and source blocks.

Control flow contribution: the header itself has no runtime loop, but its layout enables `book3s_xics.c` to perform atomic ICP updates and locked ICS source updates. IRQ numbers are split by `KVMPPC_XICS_ICS_SHIFT`; the high bits choose the ICS and the low bits choose the source index.

State and persistence: constants define the source space, reserved IRQ floor, `MASKED` priority, P/Q bits, and resend-map size. Real-mode action bits (`XICS_RM_KICK_VCPU`, `XICS_RM_CHECK_RESEND`, `XICS_RM_NOTIFY_EOI`) persist until virtual-mode completion.

Dependencies and integration: declarations for `xics_rm_h_xirr()`, `xics_rm_h_xirr_x()`, `xics_rm_h_ipi()`, `xics_rm_h_cppr()`, and `xics_rm_h_eoi()` connect C XICS code with optional real-mode assembly/C implementations. The header is compiled only under `CONFIG_KVM_XICS`.

Risks: bitfield packing in `union kvmppc_icp_state` is assumed to fit in `unsigned long` and to be safe for `cmpxchg64()` usage in the C file. Changing constants affects migration ABI and device-attribute validation. `kvmppc_xics_find_server()` is simple but O(vCPU count).

Test signals: compile both XICS-enabled and disabled configs, migration state get/set, high IRQ numbers near `KVMPPC_XICS_MAX_ICS_ID`, reserved IRQ rejection below `KVMPPC_XICS_FIRST_IRQ`, real-mode completion paths, and atomic ICP state packing on supported PPC word sizes.
