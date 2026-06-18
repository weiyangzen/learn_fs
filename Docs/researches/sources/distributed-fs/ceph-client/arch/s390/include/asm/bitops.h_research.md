<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h

Purpose: Implements s390 bit testing, inverted bit numbering helpers, and find/ffs primitives.

Important APIs/types/functions: `arch_test_bit()`, inverted bitmap helpers, `find_first_bit_inv()`, `find_next_bit_inv()`, `__flogr()`, `ffs()`, and generic non-atomic bitop mappings. Source-visible declarations include: #define _S390_BITOPS_H; #define arch___set_bit generic___set_bit; #define arch___clear_bit generic___clear_bit; #define arch___change_bit generic___change_bit; #define arch___test_and_set_bit generic___test_and_set_bit; #define arch___test_and_clear_bit generic___test_and_clear_bit; #define arch___test_and_change_bit generic___test_and_change_bit; #define arch_test_bit_acquire generic_test_bit_acquire; static __always_inline bool arch_test_bit(unsigned long nr, const volatile unsigned long *ptr); unsigned long mask;.

Control flow: Regular bitops mostly use generic helpers; inverted helpers translate bit numbers for s390/MSB-oriented hardware masks; `flogr`-based helpers find leading set bits.

State and persistence behavior: State is caller-owned bitmap memory.

Dependencies and integration points: Direct includes are #include <linux/typecheck.h>, #include <linux/compiler.h>, #include <linux/types.h>, #include <asm/asm.h>, #include <asm-generic/bitops/atomic.h>, #include <asm-generic/bitops/non-instrumented-non-atomic.h>, #include <asm-generic/bitops/lock.h>, #include <asm-generic/bitops/builtin-ffs.h>. Integrated with Integrates channel masks, facility masks, CPU masks, generic bitmap code, and architecture instruction helpers..

Risks: Inverted bit numbering is easy to misuse; mixing normal and inverted helpers corrupts hardware-visible masks.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 216 lines, 6073 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/bitops.h -->
