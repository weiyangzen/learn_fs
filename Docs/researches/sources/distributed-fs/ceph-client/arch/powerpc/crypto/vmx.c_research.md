# sources/distributed-fs/ceph-client/arch/powerpc/crypto/vmx.c

Purpose: registers the Power8 VMX/Vector Crypto AES skcipher implementations with the Linux crypto API when the CPU advertises vector crypto support.

Important APIs/types/functions: `p8_init()` registers `p8_aes_cbc_alg`, `p8_aes_ctr_alg`, and `p8_aes_xts_alg`; `p8_exit()` unregisters them in reverse order. `module_cpu_feature_match(PPC_MODULE_FEATURE_VEC_CRYPTO, p8_init)` gates module initialization on the CPU feature.

Control flow: initialization attempts CBC registration first, then CTR, then XTS. Each failure jumps to a rollback label that unregisters previously registered algorithms before returning the error. Exit unconditionally unregisters XTS, CTR, and CBC.

State and persistence: state lives in the crypto algorithm registry for the module lifetime. This file owns no private persistent data and relies on algorithm objects declared in `aesp8-ppc.h`.

Dependencies and integration points: includes module, CPU feature, and crypto skcipher headers, plus `<asm/cputable.h>`. It integrates with the kernel crypto manager, module loader, and Power8 AES assembly/C glue.

Risks: registration order must match rollback and exit order to avoid leaked or double-unregistered algorithms. The module is useful only when `PPC_MODULE_FEATURE_VEC_CRYPTO` matches actual hardware and kernel vector state handling is correct.

Test signals: build the module, load it on Power8 or later hardware with vector crypto, and verify `cbc(aes)`, `ctr(aes)`, and `xts(aes)` self-tests and crypto API listings. Negative tests should force registration failure and confirm rollback leaves no partial algorithms.
