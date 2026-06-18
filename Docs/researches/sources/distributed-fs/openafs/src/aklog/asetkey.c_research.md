# sources/distributed-fs/openafs/src/aklog/asetkey.c

## Purpose
`asetkey.c` implements the `asetkey` administrative command for adding, deleting, listing, and randomly generating OpenAFS server keys in the server configuration directory. It supports legacy rxkad DES keys, rxkad Kerberos 5 typed keys, and rxgk typed keys.

## Important APIs, types, and functions
The command verbs are dispatched in `main` to `addKey`, `deleteKey`, `listKey`, and `addRandomKey`. Key construction helpers include `stringToType`, `keyFromCommandLine`, `keyFromKeytab`, and `random_key`; display helpers include `printKey`. It uses `afsconf_typedKey_new`, `afsconf_AddTypedKey`, `afsconf_DeleteKey`, `afsconf_DeleteKeyByType`, `afsconf_DeleteKeyBySubType`, `afsconf_GetAllKeys`, and `afsconf_typedKey_values`.

## Control flow
`main` opens `AFSDIR_SERVER_ETC_DIRPATH` with `afsconf_Open`, validates a verb, and delegates. `addKey` supports old forms (`add <kvno> <hexkey>` and `add <kvno> <keytab> <principal>`) plus typed forms (`add <type> <kvno> <subtype> <hexkey>` and keytab equivalents). `keyFromKeytab` initializes Kerberos, parses the principal, reads the requested service key from a keytab, and wraps the bytes in an `afsconf_typedKey`. For rxkad it tries DES-CBC-CRC, MD5, then MD4. `addRandomKey` generates a Kerberos random keyblock, defaulting to AES128 CTS HMAC SHA1 unless a subtype is specified. `listKey` iterates all typed keys and prints key type, kvno, enctype/subtype, and hex material.

## State and persistence
The persistent state is the server KeyFile/KeyFileExt material managed through the `afsconf` key APIs under the server config directory. Commands overwrite existing keys when adding (`afsconf_AddTypedKey(..., 1)`). The process holds transient Kerberos contexts, parsed principals, keyblocks, and typed-key references.

## Dependencies and integration points
The file integrates with OpenAFS `cellconfig` and `keys` APIs, Kerberos keytab and random-key APIs, rx opaque buffers, and com_err reporting. It is an administrative producer for the keys later consumed by `authcon.c` and server-side rxkad/rxgk authentication.

## Risks
`char2hex` returns `-1` for invalid characters, but `keyFromCommandLine` does not reject that before combining nibbles, so malformed hex can become unintended key bytes. The command prints key material in full during `list`, which is expected for a key management tool but sensitive in logs. Several failure paths exit immediately; that is normal for a CLI but leaves no structured error recovery. Keytab extraction must match kvno/enctype precisely, especially for typed rxgk/rxkad_krb5 keys.

## Test signals
Tests should add/list/delete rxkad hex keys, typed rxkad_krb5/rxgk keys, random keys with default and explicit enctypes, keytab imports for found and missing principals, malformed key lengths, invalid key types, and persistence visible to `afsconf_GetAllKeys`.
