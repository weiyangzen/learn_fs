<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h

## Purpose
Defines SH platform hooks for `rtc` memory, power, reset, or timekeeping integration.

## Important APIs, Types, And Functions
Includes `cpu/rtc.h`. Key macros/constants include `_ASM_RTC_H`, `RTC_CAP_4_DIGIT_YEAR`. Structures include `sh_rtc_platform_info`. Register or hardware-address constants include `_ASM_RTC_H`, `RTC_CAP_4_DIGIT_YEAR`.

## Control Flow
The file is primarily a declarative include-time contract. Runtime behavior occurs in generic Linux subsystems or architecture C/assembly files that consume the constants, types, macros, and prototypes here.

## State And Persistence
No persistent state is owned by this file. It provides constants or declarations for state owned by generic kernel objects, architecture implementation files, or hardware.

## Dependencies And Integration Points
It directly depends on `cpu/rtc.h`. Integration points are generic Linux headers and SH implementation files that include this architecture hook.

## Risks And Edge Cases
The main risk is ABI-like drift: generic code assumes these constants and declarations match SH implementation files, UAPI headers, and hardware behavior.

## Test Signals
Useful signals are compile coverage under the relevant Kconfig combinations plus targeted subsystem tests for the generic Linux code that includes this file.

Source read size: 13 lines, 226 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/rtc.h -->
