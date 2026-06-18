# sources/distributed-fs/openafs/src/auth/keys.c

## Purpose
Implements OpenAFS configuration-directory key management. It maintains an in-memory typed key store and persists keys to the legacy `KeyFile` for rxkad DES keys and `KeyFileExt` for newer typed keys such as rxgk.

## Important APIs, Types, and Functions
Defines private `afsconf_typedKey`, `keyTypeList`, `kvnoList`, and `subTypeList` structures. Public/key exported routines include `_afsconf_InitKeys`, `_afsconf_LoadKeys`, `_afsconf_FreeAllKeys`, `afsconf_GetKeys`, `afsconf_GetLatestKey`, `afsconf_GetKey`, rxgk lookup helpers, `afsconf_AddKey`, `afsconf_DeleteKey`, `afsconf_GetKeysByType`, `afsconf_GetAllKeys`, `afsconf_GetKeyByTypes`, `afsconf_GetLatestKeysByType`, `afsconf_GetLatestKeyByTypes`, `afsconf_AddTypedKey`, `afsconf_DeleteKeyByType`, `afsconf_DeleteKeyBySubType`, and typed-key reference/value helpers. `addMemoryKey`, `findByType`, `findByKvno`, and `findBySubType` are the sorted-list core.

## Control Flow
Loading clears `dir->keyList`, parses legacy rxkad keys from `AFSDIR_KEY_FILE`, then parses all non-rxkad typed records from `AFSDIR_EXT_KEY_FILE`. Mutations validate constraints, update the in-memory list, save both disk files, and touch the config directory. Lookups call `_afsconf_Check`, find the relevant type/kvno/subtype, and return reference-counted key objects or lists.

## State and Persistence
The authoritative runtime state is `dir->keyList`, a three-level sorted queue by type, kvno, and subtype. On disk, rxkad remains in the old fixed `nkeys + kvno + 8-byte key` format; extended keys are variable-length records with network-byte-order metadata and key material. Typed keys use atomic refcounts and `rx_opaque` ownership.

## Dependencies and Integration Points
Integrates with `cellconfig` configuration directories, global auth locking, OPR queues, RX atomic/opaque helpers, rxgk key conversion when enabled, and the old `struct afsconf_keys` compatibility API consumed by legacy tools.

## Risks and Test Signals
Read errors return `EIO` and clear loaded keys, but writes truncate files directly before completing, so partial write failures can leave damaged key files. Legacy rxkad compatibility assumes 8-byte key material and single subtype. `afsconf_DeleteKeyBySubType` has early `return AFSCONF_NOTFOUND` paths while holding `LOCK_GLOBAL_MUTEX`, a lock-risk worth auditing. Tests should cover malformed KeyFileExt records, duplicate overwrite behavior, rxkad max-8 enforcement, bcrypt kvno 999 latest-key skipping, and lock release on all error paths.
