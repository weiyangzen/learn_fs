# sources/distributed-fs/ceph-client/security/ipe/hooks.h

Purpose: Declares IPE LSM hook functions, hook enum identifiers, and optional integrity blob hook interfaces.

Important APIs/types/functions: Defines `enum ipe_hook_type` and `IPE_HOOK_INVALID`, then prototypes all hook handlers implemented in `hooks.c`.

Control flow: No runtime logic; enum values must stay aligned with audit hook name array in `audit.c`.

State and persistence: No state.

Dependencies and integration: Includes kernel file/binfmt/security/block/fsverity types and is used by `ipe.c`, `eval.c`, and `audit.c`.

Risks and test signals: Risks include enum/name mismatch and missing prototypes under config guards. Build and audit output tests cover this.
