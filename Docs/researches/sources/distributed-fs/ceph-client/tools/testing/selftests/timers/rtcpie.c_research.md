# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/rtcpie.c

## Purpose
This RTC test validates periodic interrupt emulation through `/dev/rtc0` or a user-provided RTC device. It confirms that periodic IRQ rates can be read/set and that reads block roughly for the configured interrupt period.

## Important APIs, Types, and Functions
The test uses `/dev/rtc*`, `ioctl(RTC_IRQP_READ)`, `RTC_IRQP_SET`, `RTC_PIE_ON`, `RTC_PIE_OFF`, blocking `read()`, and `gettimeofday()`. It stores and restores the old periodic interrupt rate.

## Control Flow
`main()` chooses the RTC path, skips if the default device is absent, opens the device, reads the current PIE rate, then loops through 2, 4, 8, 16, 32, and 64 Hz. For each rate it enables periodic interrupts, reads 20 events, measures the time between reads, fails if the interval exceeds 110% of the expected period, disables interrupts, and finally restores the old rate.

## State and Persistence
Kernel RTC PIE state and rate are modified temporarily. The old rate is restored in the `done` path, but hard failures before that path can leave the device in an altered state until process exit or subsequent cleanup.

## Dependencies and Integration Points
The test depends on Linux RTC UAPI definitions, an RTC class device, and permissions to change requested PIE rates. It integrates as a kselftest-style standalone executable but prints most progress directly to stderr.

## Risks
Some RTC devices do not support periodic IRQs or changing the rate; those cases go to the successful `done` path instead of failing. Timing is sensitive to scheduler delays. Privilege restrictions can affect higher rates, though this test only uses 2 to 64 Hz.

## Test Signals
The main signal is 20 blocking reads per rate with measured intervals near the configured period. `EINVAL` from RTC IRQ operations indicates unsupported functionality rather than a kernel regression for devices without PIE support.
