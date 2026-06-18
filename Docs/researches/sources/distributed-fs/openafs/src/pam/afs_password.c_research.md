<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_password.c -->
# sources/distributed-fs/openafs/src/pam/afs_password.c

## Purpose
Implements `pam_sm_chauthtok` for changing a user's legacy AFS/KA password. It verifies the old password, prompts for a new password twice, obtains an admin token, connects to the KA maintenance service, and submits the password change.

## Important APIs, Types, And Functions
The hook uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_set_item`), OpenAFS KA/RX APIs (`ka_VerifyUserPassword`, `ka_Init`, `rx_Init`, `ka_LocalCell`, `ka_StringToKey`, `ka_GetAdminToken`, `ka_AuthServerConn`, `ka_ChangePassword`), `ktc` token/key structs, message/prompt helpers, and NSS lookup. Options include `debug`, `nowarn`, `use_first_pass`, `try_first_pass`, and `ignore_root`.

## Control Flow
The function parses options, obtains conversation and user, optionally ignores root, gets or prompts for the old password, verifies it with `KA_USERAUTH_DOSETPAG`, saves it as `PAM_AUTHTOK`/`PAM_OLDAUTHTOK`, returns success immediately for `PAM_PRELIM_CHECK`, requires `PAM_UPDATE_AUTHTOK` for the update phase, prompts for and confirms a non-empty new password, initializes KA/RX, resolves the local cell, derives old/new keys, gets a short admin token, connects to the KA maintenance service, and calls `ka_ChangePassword`.

## State And Persistence
Successful execution changes the user's AFS password in the KA database and updates `PAM_AUTHTOK` to the new password. Old and new password buffers are partially wiped on error paths; prompted strings are owned by PAM conversation allocation.

## Dependencies And Integration Points
This is exported by the PAM module for password stacks and depends on legacy kaserver infrastructure. It integrates with the same message/prompt utilities as authentication and with KA maintenance RPCs.

## Risks And Test Signals
Risks include deprecated KA password handling, fixed 256-byte buffers for passwords/realm/cell, incomplete wiping/freeing of new password on success, password quality delegated elsewhere, and lack of alternate-cell option support despite auth/setcred supporting it. Test signals include prelim/update PAM phases, wrong old password, mismatched new passwords, KA server unavailability, successful password change, and PAM_AUTHTOK update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_password.c -->
