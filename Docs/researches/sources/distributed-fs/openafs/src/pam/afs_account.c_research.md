<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_account.c -->
# sources/distributed-fs/openafs/src/pam/afs_account.c

## Purpose
Implements the PAM account-management hook for the OpenAFS PAM module. It currently accepts all account-management checks unconditionally.

## Important APIs, Types, And Functions
The only exported function is `pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv)`, returning `PAM_SUCCESS`. It includes PAM application/module headers and OpenAFS config headers.

## Control Flow
There is no option parsing or external call. PAM invokes the account hook and the module immediately reports success.

## State And Persistence
No state is read, written, or persisted.

## Dependencies And Integration Points
The function is exported by the PAM modules built in `Makefile.in` and appears in the module export map. It lets OpenAFS participate in PAM account stacks without imposing account restrictions.

## Risks And Test Signals
The risk is policy ambiguity: account expiry/access checks must come from other PAM modules because this one never rejects. Test signals are compile/export coverage and PAM stack behavior where account management succeeds after authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_account.c -->
