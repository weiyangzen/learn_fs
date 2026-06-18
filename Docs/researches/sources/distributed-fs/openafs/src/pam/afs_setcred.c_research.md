<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_setcred.c -->
# sources/distributed-fs/openafs/src/pam/afs_setcred.c

## Purpose
Implements `pam_sm_setcred` for establishing or refreshing AFS credentials after successful authentication. It retrieves the password saved by `pam_sm_authenticate`, ensures a PAG exists, obtains or refreshes tokens, and optionally exports password-expiry and Kerberos ticket-file environment variables.

## Important APIs, Types, And Functions
The hook uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_get_data`, `pam_putenv`), OpenAFS APIs (`setpag`, `ktc_newpag`, `getPAG`, `ka_VerifyUserPassword`, `ka_UserAuthenticateGeneral`, `ktc_ForgetAllTokens`), optional Kerberos `ktc_tkt_string`, helper `do_klog`, and message/prompt utilities. It handles PAM flags `PAM_DELETE_CRED`, `PAM_REINITIALIZE_CRED`, `PAM_REFRESH_CRED`, and `PAM_ESTABLISH_CRED`.

## Control Flow
Options are parsed similarly to auth, including `cell`, `ignore_uid`, `refresh_token`, `use_klog`, and `setenv_password_expires`. Delete and reinitialize requests currently return success without modifying tokens. Establish/refresh retrieves the stored password or prompts if allowed, creates a PAG if not refreshing and none exists, verifies for refresh or obtains tokens for establish using either KA calls or external `klog`, supports retry after first-pass failure, then on success may set `PASSWORD_EXPIRES` and `KRBTKFILE`.

## State And Persistence
Successful establish/refresh creates AFS tokens in the current PAG. It may create a new PAG, set PAM environment variables, and chown a Kerberos ticket file to the local user's uid/gid in Kerberos builds. It wipes only locally copied prompt passwords.

## Dependencies And Integration Points
This is the credential half of the PAM module and depends on `afs_auth.c` storing the password under `pam_afs_lh`. It integrates with KA servers, optional `klog`, Kerberos ticket handling, and PAM session/application environment propagation.

## Risks And Test Signals
Risks include returning success for delete/reinitialize without token deletion, password retention through PAM data, fixed-size buffers, duplicate option parsing, and inconsistent behavior between KA and klog modes. Test signals include establish vs refresh flows, missing saved password, alternate cell, ignored UIDs, PAG creation only when needed, `PASSWORD_EXPIRES` and `KRBTKFILE` environment setting, and token presence after login.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_setcred.c -->
