<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h

Purpose: Declares s390 busy-wait delay helpers.

Important APIs/types/functions: `__ndelay()`, `__udelay()`, `__delay()`, and `ndelay/udelay/mdelay` macros. Source-visible declarations include: #define _S390_DELAY_H; void __ndelay(unsigned long nsecs);; void __udelay(unsigned long usecs);; void __delay(unsigned long loops);; #define ndelay(n) __ndelay((unsigned long)(n)); #define udelay(n) __udelay((unsigned long)(n)); #define mdelay(n) __udelay((unsigned long)(n) * 1000).

Control flow: Callers request nanosecond/microsecond/millisecond busy waits that implementation calibrates against s390 timers.

State and persistence behavior: No state in this header; calibration state lives in implementation/time code.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates driver polling, early boot waits, and generic delay API..

Risks: Busy waits are timing-sensitive and can overflow if macro arguments are too large.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 24 lines, 647 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/delay.h -->
