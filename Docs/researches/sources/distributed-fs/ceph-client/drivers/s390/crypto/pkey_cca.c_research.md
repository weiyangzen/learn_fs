## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_cca.c

Purpose: implements the CCA protected-key handler. It recognizes CCA AES data, CCA AES cipher, and CCA ECC private key blobs; finds suitable APQNs; generates or imports CCA secure keys; converts CCA keys to protected keys; and verifies CCA key metadata.

Important APIs/types/functions: handler callbacks are `is_cca_key()`, `is_cca_keytype()`, `cca_apqns4key()`, `cca_apqns4type()`, `cca_key2protkey()`, `cca_gen_key()`, `cca_clr2key()`, `cca_verifykey()`, and `cca_slowpath_key2protkey()`. It registers `cca_handler` with the pkey base. When modular, AP device ids cover CEX4 through CEX8.

Control flow: APQN discovery extracts MKVPs from token formats and calls `cca_findcard2()` with appropriate minimum hardware type and master-key set. Key conversion validates token structure, waits for zcrypt operational state, discovers APQNs if wildcard/none were supplied, and tries candidate APQNs until CCA conversion succeeds. Key generation and clear-to-key validate type/subtype/size, discover APQNs if needed, then call CCA zcrypt helpers. Slowpath protected-key conversion builds a CCA data secure key from a clear-key token and converts that secure key to a protected key, retrying once.

State and persistence: only the static handler table persists. Sensitive intermediate secure keys in slowpath are stack-local and short-lived. APQN lists are bounded by `MAXAPQNSINLIST`.

Dependencies and integration: depends on zcrypt CCA misc helpers, AP device types, pkey base registry, pkey token definitions, and module CPU feature infrastructure indirectly through pkey base.

Risks and test signals: risks include token length/version validation, wildcard APQN semantics, current versus alternate MKVP matching, min hardware type selection, and clear-key slowpath policy (`PKEY_XFLAG_NOCLEARKEY`). Test CCA AES data/cipher/ECC verification, current/alternate MKVP APQN discovery, explicit and wildcard APQNs, CEX generation by subtype, no-memory flags, and malformed token rejection.
