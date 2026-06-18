# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_ep11.c

Purpose: implements the s390 pkey handler for EP11 secure key material. It recognizes EP11 non-CCA AES/ECC tokens, discovers suitable APQNs, generates EP11 AES secure keys, imports clear AES material into EP11 blobs, converts EP11 blobs into protected keys, verifies tokens, and registers those operations with the pkey core.

Important APIs and functions: `is_ep11_key()` and `is_ep11_keytype()` are pkey handler predicates. `ep11_apqns4key()` and `ep11_apqns4type()` call `ep11_findcard2()` after `zcrypt_wait_api_operational()` to find cards/domains matching EP11 API level, wrapping key verification pattern, and WKVP. `ep11_key2protkey()` validates token layout using `ep11_check_aes_key*()`/`ep11_check_ecc_key_with_hdr()` and calls `ep11_kblob2protkey()` over explicit or discovered APQNs. `ep11_gen_key()` and `ep11_clr2key()` generate secure blobs through `ep11_genaeskey()` and `ep11_clr2keyblob()`. `ep11_verifykey()` reports key subtype, bitsize, matching APQN, and current-MKVP flag. `ep11_slowpath_key2protkey()` turns clear AES tokens into temporary EP11 keys before converting to protected keys.

Control flow: callers enter through the `pkey_handler` table registered at module init. Most paths first reject malformed token headers, unsupported key types, incompatible subtypes, or invalid clear-key lengths. If APQNs are unspecified or wildcarded, the handler discovers candidate EP11 queues; then it iterates candidates until one hardware operation succeeds or all fail.

State and persistence: this file keeps no persistent key state. It uses stack buffers for APQN lists and temporary EP11 blobs. Module lifetime state is only the registered `ep11_handler`; AP hardware state and key wrapping keys live outside this file.

Dependencies and integration: depends on `pkey_base.h`, CCA/EP11 zcrypt helpers, AP bus card types, and secure-execution detection via `ap_is_se_guest()`. It integrates as an optional pkey provider and exposes AP modaliases for CEX4 through CEX8 when built as a module.

Risks: token length and header interpretation are critical because hardware helpers consume binary blobs. Clear-key slow path must honor `PKEY_XFLAG_NOCLEARKEY`; failures would expose policy bypass. APQN discovery is constrained to CEX7/API v4 or v6 for PKEY-extractable blobs, so regressions could silently reduce availability.

Test signals: exercise EP11 AES legacy and with-header tokens, ECC with-header verification, wildcard APQN conversion, explicit APQN fallback, extractable/non-extractable blobs, secure-execution API selection, invalid subtype/keybitsize paths, and clear-key slow path with and without `NOCLEARKEY`.
