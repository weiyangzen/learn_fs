<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h

**Purpose:** Supplies Alpha machine parameters for the kernel's soft-float library: word size, multiplication/division meat macros, NaN selection, rounding modes, and exception flags.

**Important APIs/types/functions:** `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_MUL_MEAT_*`, `_FP_DIV_MEAT_*`, `_FP_NANFRAC_*`, `_FP_CHOOSENAN`, `FP_ROUNDMODE`, `FP_RND_*`, `FP_EX_*`, `FP_DENORM_ZERO`, and `FP_INHIBIT_RESULTS`.

**Control flow:** Soft-float operations include this header so generic `soft-fp` code expands arithmetic with Alpha word width, FPCR rounding fields, and IEEE software-control flags.

**State and persistence behavior:** No local state; it reads caller-provided `mode` and `swcr` variables and maps exceptions to Alpha IEEE control bits.

**Dependencies and integration points:** Depends on Alpha FPU UAPI flags and generic soft-fp macros from the imported library.

**Risks:** NaN and rounding behavior are ABI-visible for emulated FP traps. The comment notes Alpha preference for NaN operands; changing it can alter numeric results.

**Test signals:** Soft-float exception/rounding tests, FP trap emulation, NaN propagation, denormal handling, and cross-checks against hardware FP where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/sfp-machine.h -->
