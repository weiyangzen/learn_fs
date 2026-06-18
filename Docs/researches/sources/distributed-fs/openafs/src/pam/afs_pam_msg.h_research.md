<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.h -->
# sources/distributed-fs/openafs/src/pam/afs_pam_msg.h

## Purpose
Declares the PAM conversation helper functions used by the OpenAFS PAM module.

## Important APIs, Types, And Functions
The header declares `pam_afs_printf(PAM_CONST struct pam_conv *, int error, int fmt_msgid, ...)` and `pam_afs_prompt(PAM_CONST struct pam_conv *, char **response, int echo, int fmt_msgid, ...)`.

## Control Flow
There is no implementation control flow. The declarations define the shared interface for message display and prompting.

## State And Persistence
No state is stored by this header.

## Dependencies And Integration Points
It depends on PAM types from included callers and pairs with `afs_pam_msg.c`; auth, setcred, and password-change files include it.

## Risks And Test Signals
Risks are declaration drift and missing PAM type definitions in unusual include orders. Test signals are clean compilation of all PAM modules and prompt calls linking against `afs_pam_msg.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.h -->
