<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h

Purpose: Provides inline support for DIAG 288 watchdog control.

Important APIs/types/functions: Watchdog intervals, function codes, restart action constants, and `__diag288()`. Source-visible declarations include: #define _ASM_S390_DIAG288_H; #define MIN_INTERVAL 15 /* Minimal time supported by diag288 */; #define MAX_INTERVAL 3600 /* One hour should be enough - pure estimation */; #define WDT_DEFAULT_TIMEOUT 30; #define WDT_FUNC_INIT 0; #define WDT_FUNC_CHANGE 1; #define WDT_FUNC_CANCEL 2; #define WDT_FUNC_CONCEAL 0x80000000; #define LPARWDT_RESTART 0; static inline int __diag288(unsigned int func, unsigned int timeout,.

Control flow: `__diag288()` passes function, timeout, action, and command length/address operands to the DIAG 288 instruction and returns the condition/result code.

State and persistence behavior: State is hypervisor watchdog configuration and caller command buffers.

Dependencies and integration points: Direct includes are #include <asm/asm-extable.h>, #include <asm/types.h>. Integrated with Integrates s390 watchdog drivers, LPAR/z/VM firmware, and reboot/restart policy..

Risks: Timeout bounds must follow DIAG support; wrong conceal/cancel/change function use can leave watchdogs armed unexpectedly.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 41 lines, 1031 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag288.h -->
