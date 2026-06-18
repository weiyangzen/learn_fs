<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h

Purpose: Defines CP Assist for Cryptographic Functions opcodes, function codes, query helpers, and inline instruction wrappers.

Important APIs/types/functions: `cpacf_mask_t`, `cpacf_qai_t`, `cpacf_query()`, `cpacf_query_func()`, `cpacf_qai()`, and wrappers for KM/KMC/KIMD/KLMD/KMAC/KMCTR/PRNO/TRNG/PCC/PCKMO/KMA. Source-visible declarations include: #define _ASM_S390_CPACF_H; #define CPACF_KMAC 0xb91e /* MSA */; #define CPACF_KM 0xb92e /* MSA */; #define CPACF_KMC 0xb92f /* MSA */; #define CPACF_KIMD 0xb93e /* MSA */; #define CPACF_KLMD 0xb93f /* MSA */; #define CPACF_PCKMO 0xb928 /* MSA3 */; #define CPACF_KMF 0xb92a /* MSA4 */; #define CPACF_KMO 0xb92b /* MSA4 */; #define CPACF_PCC 0xb92c /* MSA4 */.

Control flow: Query helpers validate the opcode against facility bits, execute the query subfunction, and test function-code masks. Operation wrappers load fixed GR pairs, issue CPACF instructions, and loop on partial completion condition codes.

State and persistence behavior: State is CPACF hardware state, parameter blocks, source/destination buffers, and crypto context data supplied by callers.

Dependencies and integration points: Direct includes are #include <asm/facility.h>, #include <linux/kmsan-checks.h>. Integrated with Integrates kernel crypto drivers, protected-key support, random/entropy code, facility probing, KMSAN annotations, and condition-code helper macros..

Risks: Opcode/function availability must be checked before use. Partial-completion loops, parameter-block layouts, and KMSAN unpoisoning for TRNG are correctness and security critical.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 736 lines, 22050 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpacf.h -->
