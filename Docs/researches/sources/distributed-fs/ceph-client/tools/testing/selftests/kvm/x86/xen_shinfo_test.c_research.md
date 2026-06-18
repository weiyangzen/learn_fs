<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c

## Purpose
This large Xen HVM selftest validates KVM's Xen shared-info, vCPU info, runstate, event-channel, timer, hypercall, poll, and clock integration. It also stress-tests shared-info cache locking while event delivery and polling race with host attribute updates.

## Important APIs, Types, and Functions
Important guest-side structures mirror Xen ABI layout: `struct shared_info`, `struct vcpu_info`, `struct pvclock_vcpu_time_info`, `struct pvclock_wall_clock`, `struct vcpu_runstate_info`, `struct compat_vcpu_runstate_info`, `struct evtchn_send`, and `struct sched_poll`. Key functions are `evtchn_handler()`, `guest_wait_for_irq()`, `guest_code()`, `juggle_shinfo_state()`, and `handle_alrm()`. Host code uses `KVM_CAP_XEN_HVM`, `KVM_XEN_HVM_CONFIG`, `KVM_XEN_HVM_SET_ATTR`, `KVM_XEN_VCPU_SET_ATTR`, `KVM_XEN_HVM_EVTCHN_SEND`, `KVM_SET_GSI_ROUTING`, irqfd/eventfd, Xen hypercall interception, and `KVM_GET_CLOCK`.

## Control Flow, State, and Persistence
`main()` detects Xen HVM capability flags, creates a VM, maps a three-page shared-info region, configures Xen long mode, shared-info via GPA or HVA, vCPU info, pvclock info, upcall vector, optional runstate, IRQ routes, eventfds, and a Xen timer port. The guest executes a long staged script: host-injected upcall vector, runstate current/adjust/data checks, steal-time generation, masked and unmasked event-channel delivery, slow paths after memslot changes, ioctl-based event send, guest `EVTCHNOP_send` hypercalls, eventfd-backed event channels, one-shot timer setup/restore/past-expiry tests, `SCHEDOP_poll` ready/timeout/masked/wake paths, vCPU-info HVA setup, and shared-info locking races. The host loop handles each sync by mutating shared info, setting attributes, writing eventfds, arming timers, or checking expected IRQ delivery. After the guest finishes, the host resets event channels, sanity-checks Xen wallclock and pvclock versions against `KVM_GET_CLOCK`, and exercises runstate writes across a page boundary in both compatibility and long mode.

## Dependencies and Integration Points
The test integrates with the KVM Xen HVM ABI, shared-info caching by GFN/HVA, event-channel routing and irqfd, Xen hypercall interception for `event_channel_op`, `sched_op`, and `set_timer_op`, vCPU runstate accounting, pvclock/wallclock generation, memslot invalidation slow paths, pthread cancellation, alarms for timeout diagnostics, and host scheduler run-delay observation.

## Risks and Test Signals
Risks include stale shared-info mappings after HVA remap or memslot changes, lost event-channel interrupts, incorrect pending/mask bits, timer IRQ drops while shinfo is invalid, runstate structure overruns at page boundaries, clock version instability, and lock corruption under concurrent shared-info attr updates. Signals are every staged `GUEST_SYNC`, `TEST_GUEST_SAW_IRQ` only when expected, successful poll/timer wake behavior, sane pvclock/wallclock versions, runstate sums matching state-entry time, and clean completion of shared-info race threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c -->
