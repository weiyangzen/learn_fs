# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_sysfs.c

Purpose: defines the pkey module's read-only binary sysfs attributes for generating fresh protected keys and secure-key blobs. Attributes are grouped into `protkey`, `ccadata`, `ccacipher`, and `ep11`, each returning a fixed-size binary token or padded blob.

Important APIs and functions: `sys_pkey_handler_gen_key()` wraps `pkey_handler_gen_key()` and requests handler modules on `-ENODEV` before retrying. `pkey_protkey_aes_attr_read()`, `pkey_protkey_aes_xts_attr_read()`, and `pkey_protkey_hmac_attr_read()` build protected-key tokens. `pkey_ccadata_aes_attr_read()` generates CCA data key tokens. `pkey_ccacipher_aes_attr_read()` generates CCA cipher key tokens sized by `CCACIPHERTOKENSIZE`. `pkey_ep11_aes_attr_read()` generates EP11 AES blobs padded to `MAXEP11AESKEYBLOBSIZE`. `pkey_attr_groups` exports all attribute groups to the pkey device.

Control flow: sysfs invokes a concrete `*_read()` function for each binary attribute. Each reader rejects partial reads with `off != 0` or too-small `count` because every read generates new random key material. XTS attributes generate two independent tokens/blobs and concatenate them.

State and persistence: no generated key is persisted by this file. State is transient in the sysfs output buffer and local structs. The only durable surface is the attribute table that the pkey core attaches to sysfs.

Dependencies and integration: depends on pkey core generation APIs, CCA/EP11 token constants, `BIN_ATTR_RO`, and Linux sysfs binary attribute semantics. It integrates with handler modules indirectly, causing module-load requests when no handler is available.

Risks: callers must read the full binary object in one read. Size constants are ABI-sensitive because userspace consumes exact token lengths. Any mismatch between attribute size and actual generated length can truncate or expose stale zero padding. XTS handling must avoid returning two copies of the same generated key.

Test signals: read each attribute with exact count, short count, and nonzero offset; verify XTS returns two token-sized outputs; force first `pkey_handler_gen_key()` to return `-ENODEV` and confirm retry after module request; validate fixed sizes for protected, CCA data, CCA cipher, and EP11 outputs.
