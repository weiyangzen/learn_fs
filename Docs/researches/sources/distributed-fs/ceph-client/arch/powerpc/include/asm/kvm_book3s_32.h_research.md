# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_32.h

Purpose: supplies 32-bit Book3S PR KVM shadow-vcpu access and classic segment/PTE constants.

Important APIs/types/functions: `svcpu_get()` returns `vcpu->arch.shadow_vcpu`; `svcpu_put()` is empty. Constants include `PTE_SIZE`, `VSID_ALL`, `SR_INVALID`, `SR_KP`, PTE bits (`PTE_V`, `PTE_SEC`, `PTE_M`, `PTE_R`, `PTE_C`), `SID_SHIFT`, `ESID_MASK`, `VSID_MASK`, and `VPN_SHIFT`.

Control flow: C code obtains the shadow vcpu directly from the vcpu architecture state and performs no preemption manipulation in this 32-bit path. Translation code uses the constants to decode segment registers and PTEs.

State and persistence: the only state touched is the existing `shadow_vcpu` pointer and guest segment/PTE state stored elsewhere. The constants are compile-time MMU layout values.

Dependencies and integration points: included by Book3S PR MMU code and the common Book3S accessor layer; it integrates with 32-bit hash translation and shadow-vcpu save/restore.

Risks: the empty `svcpu_put()` is intentional; adding symmetry with the 64-bit PACA path would be wrong unless the ownership model changes. Segment and PTE bit constants are architectural and must match the classic 32-bit Book3S MMU format.

Test signals: compile 32-bit Book3S KVM, boot a PR guest, exercise segment faults and BAT/segment translation, and verify shadow-vcpu state is not shared across vcpus incorrectly.
