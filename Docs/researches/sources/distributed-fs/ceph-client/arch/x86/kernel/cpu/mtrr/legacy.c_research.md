# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mtrr/legacy.c

Purpose: selects 32-bit legacy non-generic MTRR backends and registers syscore suspend/resume save/restore for those CPUs.

Important APIs/types/functions: exports `mtrr_set_if()` and `mtrr_register_syscore()`. Internal type `mtrr_value` stores one range's type, base, and size. Helpers `mtrr_save()` and `mtrr_restore()` implement syscore callbacks through `mtrr_syscore_ops`.

Control flow: `mtrr_set_if()` switches on `boot_cpu_data.x86_vendor` and feature bits, selecting `amd_mtrr_ops` for AMD K6, `centaur_mtrr_ops` for Centaur MCR, or `cyrix_mtrr_ops` for Cyrix ARR. `mtrr_register_syscore()` allocates a `num_var_ranges` save array and registers syscore callbacks. Suspend saves each backend range through `mtrr_if->get()`; resume restores non-empty ranges through `mtrr_if->set()`.

State and persistence: `mtrr_value` is heap state retained for suspend/resume. Hardware MTRR-like state is restored after resume; nothing is written to disk by this code.

Dependencies and integration points: built only for `CONFIG_X86_32`. Called from `mtrr_bp_init()` and `mtrr_init_finalize()` in `mtrr.c`. Depends on legacy backend ops and syscore infrastructure.

Risks: only legacy CPUs without generic MTRRs use this path, but allocation failure leaves save unable to proceed. Restore only writes ranges with nonzero size, so disabled slots remain whatever firmware/resume left unless backend reset behavior is acceptable. Backend selection must match CPU feature bits exactly.

Test signals: 32-bit AMD K6, Cyrix, and Centaur boot selection; suspend/resume preserving MTRR-like ranges; allocation failure handling; and builds where `CONFIG_X86_32` is disabled ensuring stubs from `mtrr.h` satisfy references.
