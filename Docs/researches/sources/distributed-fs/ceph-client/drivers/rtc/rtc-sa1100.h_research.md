# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sa1100.h

Purpose: private header for the SA1100/PXA RTC implementation. It defines the per-device state passed between the platform-specific probe path and the exported common initializer.

Important APIs/types/functions: `struct sa1100_rtc` contains the spinlock, MMIO pointers for counter/alarm/status/trim registers, 1 Hz and alarm IRQ numbers, `struct rtc_device *`, and `struct clk *`. The single function declaration is `sa1100_rtc_init(struct platform_device *pdev, struct sa1100_rtc *info)`.

Control flow/state/persistence: the header has no executable flow, but its struct defines all mutable state used by `rtc-sa1100.c`. Register pointer fields are initialized after MMIO mapping and before shared initialization; `lock` protects RTSR writes; the clock pointer is prepared/enabled by init and disabled by remove.

Dependencies/integration: includes `linux/kernel.h` for kernel types, forward-declares `struct clk` and `struct platform_device`, and is included by the local driver. It is not a user ABI.

Risks/test signals: changes to this header affect both the standalone driver and any user of the exported init symbol. Validate struct field initialization ordering, lock use around RTSR paths, and compile coverage when `sa1100_rtc_init()` is referenced externally.
