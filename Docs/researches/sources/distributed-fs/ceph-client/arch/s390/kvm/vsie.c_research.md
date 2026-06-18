# sources/distributed-fs/ceph-client/arch/s390/kvm/vsie.c

## Purpose
Implements s390 nested virtualization support through virtual SIE. It shadows a guest-provided SIE control block, constructs or reuses shadow guest address maps, pins referenced guest blocks, runs hardware SIE for guest3 where safe, and forwards/repairs intercepts back to guest2.

## Important APIs, Types, And Functions
The central type is page-sized `struct vsie_page`, containing the shadow SCB, machine-check backup, pointer to the original SCB, satellite block GPAs, cached shadow gmap, shadow CRYCB, and facility list. Public entry points are `kvm_s390_handle_vsie()`, `kvm_s390_vsie_gmap_notifier()`, `kvm_s390_vsie_init()`, `kvm_s390_vsie_destroy()`, and `kvm_s390_vsie_kick()`. Major helpers shadow CPU flags, CRYCB/APCB state, ESA mode, IBC, and SCB fields; map the prefix; pin/unpin SCB and satellite blocks; handle shadow faults, STFLE, MVPG partial execution, and SIE run loops; and manage cached `vsie_page` objects by SCB GPA.

## Control Flow And State
`kvm_s390_handle_vsie()` validates SIEF2, privilege, alignment, and pending host interrupts, obtains a cached or new `vsie_page`, pins the original SCB, shadows allowed state, pins satellite blocks, registers the shadow SCB for kicks, runs `vsie_run()`, unregisters, unpins, unshadows, and releases the page. `vsie_run()` loops over shadow-gmap acquisition, prefix mapping, intervention-request updates, and `do_vsie_run()` until guest2 or host action is needed. Shadow gmaps are cached on the page and invalidated by ASCE/EDAT changes or gmap notifier overlap with the guest prefix.

## Dependencies And Integration
Depends on SIE/SIE block layout, gmap shadow APIs, guest access, KVM SRCU, s390 facilities, crypto/AP masks, lowcore timing and branch-prediction controls, machine-check reinjection, and KVM request/kick behavior.

## Risks And Test Signals
Risks include races on original SCB fields, stale shadow gmaps, prefix mapping invalidation, incomplete state copy-back, wrong intercept forwarding, pinned-block leaks, branch-prediction isolation mistakes, and double-use of an SCB address. Signals include nested KVM boot, MVPG/STFLE nested tests, gmap notifier stress, machine-check reinjection paths, CPU kick/interrupt latency, and lockdep/RCU checks.
