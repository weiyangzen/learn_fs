# sources/distributed-fs/ceph-client/security/integrity/evm/evm_crypto.c

Purpose: calculates and updates EVM HMAC/hash values over protected security xattrs plus inode metadata, initializes the EVM HMAC key, and manages crypto hash transforms.

Important APIs, types, and functions: public functions are `evm_set_key()`, `evm_calc_hmac()`, `evm_calc_hash()`, `evm_update_evmxattr()`, `evm_init_hmac()`, and `evm_init_key()`. Internal helpers include `init_desc()`, `hmac_add_misc()`, `dump_security_xattr*()`, `evm_calc_hmac_or_hash()`, and `evm_is_immutable()`. Static state includes `evmkey`, `hmac_tfm`, `evm_tfm[]`, `mutex`, and `evm_set_key_flags`.

Control flow: `init_desc()` selects HMAC or hash algorithm, lazily allocates a crypto shash transform, sets the HMAC key when needed, and returns an initialized descriptor. `evm_calc_hmac_or_hash()` iterates configured protected xattrs, uses the requested xattr value when supplied, fetches other xattrs from VFS, feeds all values into the hash, adds inode metadata and optionally FS UUID, then finalizes. Portable signatures require an IMA xattr. `evm_update_evmxattr()` rejects immutable portable signatures, computes a SHA1 HMAC, writes `security.evm`, or removes it when no data remains. `evm_init_key()` requests the encrypted `evm-key`, passes decrypted data to `evm_set_key()`, and zeroes the original decrypted payload.

State and persistence: stores global HMAC key bytes and initialized crypto transforms. Persists calculated HMACs by setting/removing `security.evm` xattrs. Updates per-inode metadata cache for overlay/metadata inode cases. Key initialization sets `evm_initialized`.

Dependencies and integration: depends on encrypted keys, crypto shash API, EVM config xattr list, VFS xattr APIs, inode metadata, init user namespace UID/GID encoding, and EVM main/status code.

Risks and test signals: key length handling copies shorter keys but always sets a 128-byte HMAC key length, making zero padding part of the key material. HMAC input ordering and metadata encoding are compatibility-critical; changing FSUUID or protected xattrs requires relabeling. Test signals include missing key, immutable signature rejection, portable signature without IMA hash, xattr update/removal, overlay metadata cache behavior, and encrypted-key zeroization.
