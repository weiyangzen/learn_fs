<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h

Purpose: Provides common s390 inline-assembly helper macros.

Important APIs/types/functions: `__HAVE_ASM_FLAG_OUTPUTS__`, `CC_IPM`, `CC_OUT`, `CC_TRANSFORM`, `CC_CLOBBER`, and `CC_CLOBBER_LIST` variants. Source-visible declarations include: #define _ASM_S390_ASM_H; #define __HAVE_ASM_FLAG_OUTPUTS__ 1; #define CC_IPM(sym); #define CC_OUT(sym, var) "=@cc" (var); #define CC_TRANSFORM(cc) ({ cc; }); #define CC_CLOBBER; #define CC_CLOBBER_LIST(...) __VA_ARGS__; #define CC_IPM(sym) " ipm %[" __stringify(sym) "]\n"; #define CC_OUT(sym, var) [sym] "=d" (var); #define CC_TRANSFORM(cc) ({ (cc) >> 28; }).

Control flow: When compiler condition-code outputs are available, helpers bind directly to `=@cc`; otherwise they emit `ipm` and transform the upper condition-code bits.

State and persistence behavior: No state; it abstracts compiler and assembler capability differences.

Dependencies and integration points: Direct includes are #include <linux/stringify.h>. Integrated with Used by cmpxchg, CPACF, CPU-MF, and other instruction wrappers that need condition-code results..

Risks: Condition-code extraction must be consistent across compiler feature combinations or wrappers return wrong statuses.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 51 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/asm.h -->
