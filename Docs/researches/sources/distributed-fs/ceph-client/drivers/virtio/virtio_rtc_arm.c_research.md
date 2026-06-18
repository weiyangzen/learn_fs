## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_arm.c

Purpose: this Arm-specific companion supplies hardware cross-timestamp parameters for virtio RTC PTP support.

Important APIs/types/functions: it implements `viortc_hw_xtstamp_params(u8 *hw_counter, enum clocksource_ids *cs_id)`, returning `VIRTIO_RTC_COUNTER_ARM_VCT` and `CSID_ARM_ARCH_COUNTER`.

Control flow: PTP registration or cross-timestamp operations call this symbol when available. It has no branching and simply reports that the Arm virtual counter should be requested from the virtio RTC device and correlated with Linux's Arm architected clocksource.

State and persistence behavior: no state is stored. The function writes through caller-provided pointers only.

Dependencies and integration points: it depends on `linux/clocksource_ids.h`, `uapi/linux/virtio_rtc.h`, and the internal virtio RTC header. It overrides the weak fallback in `virtio_rtc_ptp.c`, which returns `-EOPNOTSUPP` on platforms without a hardware-specific implementation.

Risks: platform correctness depends on the running system actually using the Arm architected counter as the clocksource when cross timestamps are requested. Mismatches are rejected later by `ktime_get_snapshot()` checks in the PTP code.

Test signals: build with Arm virtio RTC PTP support, verify `getcrosststamp` is advertised only when the device supports `VIRTIO_RTC_COUNTER_ARM_VCT`, and verify it returns `-EOPNOTSUPP` if the active clocksource ID differs.
