# sources/distributed-fs/ceph-client/include/linux/clocksource_ids.h

Purpose: This header defines stable IDs for known clocksource bases so snapshots and coupled clock-event logic can identify the underlying time source.

Important APIs/types/functions: It exports `enum clocksource_ids` with `CSID_GENERIC`, `CSID_ARM_ARCH_COUNTER`, `CSID_S390_TOD`, `CSID_X86_TSC_EARLY`, `CSID_X86_TSC`, `CSID_X86_KVM_CLK`, `CSID_X86_ART`, and `CSID_MAX`.

Control flow: There is no runtime control flow. Clocksource drivers set IDs in `struct clocksource` or `struct clocksource_base`; consumers compare IDs when validating snapshots.

State and persistence behavior: IDs are compile-time constants and become part of internal timekeeping contracts. Adding or changing values affects cross-subsystem identification.

Dependencies and integration points: It is included by `clocksource.h` and used by architecture clocksources, VDSO/time snapshot paths, and clockevent coupled-mode metadata.

Risks: Reordering or reusing enum values can make saved IDs ambiguous. New clocksources should choose a generic or specific ID intentionally.

Test signals: Compile coverage for architecture clocksources, time snapshot validation tests, VDSO mode checks, and coupled clockevent tests are relevant.
