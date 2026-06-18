<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c

Purpose: Registers a CMOS RTC platform device for Loongson2EF platforms.

Important APIs/types/functions: `loongson_rtc_resources` describes CMOS IO ports and `RTC_IRQ`; `loongson_rtc_platform_init()` registers `rtc_cmos`.

Control flow: A `device_initcall` unconditionally registers the platform device with IO and IRQ resources.

State and persistence: Creates a platform device consumed by the generic `rtc_cmos` driver.

Dependencies and integration: Depends on `mc146818rtc` constants and platform device core.

Risks: Assumes PC-compatible CMOS ports and IRQ are present on every supported board.

Test signals: `/dev/rtc` or `rtc_cmos` should bind, and reads should match MC146818 CMOS time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c -->
