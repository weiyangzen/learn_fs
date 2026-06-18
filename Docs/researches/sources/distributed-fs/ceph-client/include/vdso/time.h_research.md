<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time.h -->
# sources/distributed-fs/ceph-client/include/vdso/time.h

Purpose: defines the time namespace offset structure shared by vDSO data pages.

Important APIs and types: `struct timens_offset` stores signed seconds and unsigned nanoseconds offsets.

Control flow: time namespace vDSO pages store per-clock offsets; namespace-aware vDSO code reads host time and applies these offsets.

State and persistence: instances are live VVAR state for time namespace mappings.

Dependencies and integration points: depends on UAPI Linux integer types and integrates with `vdso/datapage.h` and time namespace support.

Risks and test signals: risks include invalid nsec normalization and signed/unsigned arithmetic bugs. Test time namespace offsets for realtime/boottime/TAI and unaffected clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time.h -->
