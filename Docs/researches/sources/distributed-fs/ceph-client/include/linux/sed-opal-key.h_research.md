# sources/distributed-fs/ceph-client/include/linux/sed-opal-key.h

Purpose: `sed-opal-key.h` abstracts read/write access to stored Self-Encrypting Drive Opal authentication keys, allowing platform keystores to override key handling.

Important APIs/types/functions: It declares `sed_read_key(char *keyname, char *key, u_int *keylen)` and `sed_write_key(char *keyname, char *key, u_int keylen)` when `CONFIG_PSERIES_PLPKS_SED` is enabled. Otherwise both return `-EOPNOTSUPP`.

Control flow: Opal or platform code asks for a named key, receives bytes and length through caller buffers, or writes a replacement key. The actual persistent keystore access is implemented elsewhere.

State and persistence behavior: This header owns no state. Enabled implementations may persist keys in protected platform storage; disabled stubs explicitly indicate unsupported operation.

Dependencies and integration points: It depends on kernel error codes and integrates with pSeries PLPKS-backed SED boot PIN/key workflows and the Opal block layer.

Risks: Callers must size buffers correctly and handle unsupported platforms. Key material lifetime and zeroization are implementation responsibilities; APIs use raw char buffers, so misuse can leak secrets.

Test signals: Enabled and disabled config builds, missing key, key length boundary handling, read/write round trips, permission policy in the platform keystore, and secret buffer cleanup in callers.
