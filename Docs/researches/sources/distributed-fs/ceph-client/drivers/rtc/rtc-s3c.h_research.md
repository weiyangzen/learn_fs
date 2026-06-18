<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h

Purpose: defines the Samsung S3C2410-family RTC register offsets and bit masks consumed by `rtc-s3c.c`.

Important APIs/types/functions: the header provides the `S3C2410_RTCREG(x)` identity macro, interrupt pending register `S3C2410_INTP`, RTCCON bits (`RTCEN`, `CNTSEL`, `CLKRST`, `TICSEL`, `TICEN`), alarm control bits in `S3C2410_RTCALM`, alarm field offsets, and time field offsets. It has no functions or types.

Control flow: there is no runtime control flow in the header. Its constants define how the driver reads/writes MMIO registers for time, alarm, interrupt acknowledgement, and RTC controller normalization.

State and persistence: the definitions map to persistent SoC RTC hardware registers. `S3C2410_RTCALM_*EN` masks indicate which alarm fields participate in matching, and `S3C2410_INTP_ALM`/`TIC` bits identify interrupt sources to clear.

Dependencies and integration points: included directly by `rtc-s3c.c`; protected by `__ASM_ARCH_REGS_RTC_H`. The values are part of the driver ABI with Samsung S3C-compatible RTC register layouts.

Risks and test signals: incorrect offsets or masks would corrupt calendar or alarm programming across every supported S3C-compatible SoC. Because `S3C2410_RTCREG(x)` is an identity macro, all offset interpretation relies on the MMIO resource already being mapped at the RTC register base. Validate against SoC reference manuals, alarm IRQ clear behavior, RTCCON enable/disable bits, and all time/alarm register offsets used by the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-s3c.h -->
