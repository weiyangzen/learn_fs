## sources/distributed-fs/ceph-client/drivers/virtio/virtio_rtc_internal.h

Purpose: this header defines the private interfaces shared by the virtio RTC core, RTC class wrapper, PTP wrapper, and architecture-specific cross-timestamp helpers.

Important APIs/types/functions: it forward-declares `struct viortc_dev`, `struct viortc_class`, and `struct viortc_ptp_clock`. It declares core request wrappers for reading clocks, cross timestamps, cross capabilities, and alarm operations. It declares RTC class functions and PTP register/unregister functions behind `IS_ENABLED()` guards, plus `viortc_hw_xtstamp_params()` for hardware-specific cross timestamp wiring.

Control flow: compilation selects real RTC/PTP helpers when `CONFIG_VIRTIO_RTC_CLASS` or `CONFIG_VIRTIO_RTC_PTP` are enabled, otherwise inline stubs return `-ENODEV`, `ERR_PTR(-ENODEV)`, or no-op behavior. This lets the core code call helpers conditionally while preserving build coverage across configurations.

State and persistence behavior: the header stores no state. It defines ownership contracts: the core owns `viortc_dev`; RTC/PTP wrappers receive it and parent devices, then return handles used during removal.

Dependencies and integration points: includes Linux device, error, PTP clock, and type headers. It is the internal join point between `virtio_rtc_driver.c`, `virtio_rtc_class.c`, `virtio_rtc_ptp.c`, and `virtio_rtc_arm.c`.

Risks: stub return values must match caller expectations. The PTP disabled `viortc_ptp_register()` returns `NULL`, not an error pointer, and the core treats this as "not registered." RTC disabled initialization returns `ERR_PTR(-ENODEV)`.

Test signals: build matrix coverage with RTC class enabled/disabled, PTP enabled/disabled, and architecture helper present/absent.
