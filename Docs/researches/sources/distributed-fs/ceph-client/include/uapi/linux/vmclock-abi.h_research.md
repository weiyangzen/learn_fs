<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h

Purpose: defines a shared-memory VM clock ABI that exposes counter-to-real-time calibration, migration disruption markers, clock status, leap-second hints, and generation counters to guests and optionally userspace.

Important APIs and types: `struct vmclock_abi` contains constant fields (`VMCLOCK_MAGIC`, size, version, counter ID, time type), seqcount-protected mutable fields, disruption marker, flags for TAI offset, pending disruption, error validity, monotonicity, VM generation counter, and notification support. It also carries clock status, leap-smear hint, TAI offset, leap indicator, counter period/error, paired counter/time values, and VM generation counter.

Control flow, state, and persistence: readers use `seq_count` as a seqlock to obtain coherent calibration and detect migration or snapshot events through marker changes. The mapped page is shared volatile hypervisor state.

Dependencies and integration points: designed for virtualization timekeeping, vDSO-style reads, ACPI `VMCLOCK`, and virtio-rtc alignment.

Risks and test signals: risks include seqlock memory ordering, smeared UTC misuse, signed TAI offset handling, monotonicity promises during updates, and generation counter semantics. Test coherent reads under updates, live migration, snapshot restore, TSC/ARM counter calibration, and userspace mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmclock-abi.h -->
