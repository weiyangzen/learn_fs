<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c

## Purpose
Registers the XO-1 CMOS RTC platform device with OLPC-specific alarm register offsets and wake hooks.

## Important APIs, Types, And Functions
`rtc_wake_on()` and `rtc_wake_off()` manipulate XO-1 PM wake mask bit `CS5536_PM_RTC`. `xo1_rtc_init()` checks for an `olpc,xo1-rtc` device-tree node, reads MSR alarm offsets into `cmos_rtc_board_info`, registers `rtc_cmos`, disables legacy RTC probing, and marks wakeup enabled.

## Control Flow
At `arch_initcall`, the driver exits unless the OF device node exists. It then populates resources for RTC ports and IRQ8, registers the device, and updates x86 legacy RTC state.

## State And Persistence
Stores RTC board info in static data and creates a persistent platform device. Wake state is reflected in XO-1 PM wake mask.

## Dependencies And Integration Points
Depends on OF device-tree fixups, CMOS RTC driver, OLPC XO-1 PM exports, MSR alarm-offset registers, and x86 legacy RTC flags.

## Risks And Edge Cases
Missing device-tree compatibility prevents registration. Incorrect MSR values can break alarm fields. Wake hooks require XO-1 PM support to be linked.

## Test Signals
`rtc_cmos` platform device, `/dev/rtc*`, alarm wake from suspend, and `x86_platform.legacy.rtc=0` behavior validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c -->
