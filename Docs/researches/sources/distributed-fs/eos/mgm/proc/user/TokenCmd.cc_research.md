# sources/distributed-fs/eos/mgm/proc/user/TokenCmd.cc

Purpose: implements protobuf-backed token creation and token decoding in `TokenCmd`, including authorization checks, token key loading, origin restrictions, and voucher persistence.

Important APIs and types: uses `TokenProto`, `EosTok`, `SymKeyStore`, optional `EOS_MGM_TOKEN_KEYFILE`, `gOFS->_access`, `_stat`, `_mkdir`, `_chown`, `eosView->getFile`, `createFile`, and file extended attribute `sys.token`. Helper methods are `GetTokenPrefix()` and `StoreToken()`.

Control flow: `ProcessRequest()` first requires token generation to be enabled and denies token-authenticated callers. For creation, non-root users are limited to `rwx d ! +` style permissions, one-year lifetime, current owner/group, and access-checked paths; file tokens force `allowtree=false`. It loads the signing key from the current symmetric key or a daemon-owned 0400 key file. It then builds an `EosTok`, verifies origin regexes, writes the encoded token to stdout, warns if approval is required, and stores a dumped token by voucher ID. For decoding, it reads with expiry and generation enforcement, verifies origin before dumping claims, and returns errors otherwise.

State and persistence: created token dumps are persisted as EOS namespace files under `MgmProcTokenPath/uid:<uid>/YYYY/MM/DD/<voucherid>` with `sys.token` xattr and caller ownership. Directory prefixes are created as root and chowned to the user/group.

Dependencies and integration: integrates token generation, namespace access checks, symmetric key management, audit logging, allowed-token approval policy, and namespace metadata persistence.

Risks: `StoreToken()` manipulates namespace metadata through `eosView` without an explicit local lock in this function. Permission parsing allows `!` although the error message mentions `[+1]`. Multi-path tokenization on `://:` is unusual and should be tested carefully. Tests should cover disabled generation, token-authenticated denial, root versus user creation, path access for files and tree directories, lifetime cap, keyfile ownership/mode, origin regex errors, approval warning, duplicate voucher storage, decode of expired/wrong-generation tokens, and origin mismatch without claim leakage.
