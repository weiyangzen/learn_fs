# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/cc_platform.c

Purpose: Implements pseries confidential-computing capability queries for the generic Linux `cc_platform_has()` interface.

Important APIs/types/functions: Exports `cc_platform_has(enum cc_attr attr)`. It currently recognizes `CC_ATTR_MEM_ENCRYPT` and returns `is_secure_guest()`.

Control flow: A simple switch returns true for memory encryption only when the pseries secure guest/SVM helper reports protected execution. Unknown attributes return false.

State and persistence: No local state is stored. The answer is derived from architecture secure-guest state.

Dependencies and integration points: Depends on `linux/cc_platform.h`, `asm/svm.h`, and the `ARCH_HAS_CC_PLATFORM`/`PPC_SVM` configuration path. Generic DMA, memory encryption, and confidential-computing code can query this exported function.

Risks: The implementation is intentionally narrow; new attributes will silently return false until added. Incorrect `is_secure_guest()` state would affect memory encryption and DMA policy decisions.

Test signals: Secure guest boot tests, generic `cc_platform_has(CC_ATTR_MEM_ENCRYPT)` consumers, non-secure LPAR checks, and config builds with `ARCH_HAS_CC_PLATFORM` are relevant.

Source read size: 26 lines, 496 bytes.
