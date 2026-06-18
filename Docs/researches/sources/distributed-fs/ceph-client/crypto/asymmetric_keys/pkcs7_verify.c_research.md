# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_verify.c

Purpose: verifies PKCS#7 message integrity and embedded certificate chains before external trust validation. It computes content/authattr digests, checks signatures, links embedded certificates, and enforces usage-specific PKCS#7 policy.

Important APIs/types/functions: `pkcs7_digest()` computes or selects the signature message buffer, handling authenticated attributes and algorithms that take raw data. `pkcs7_get_digest()` exposes a single-signer digest. `pkcs7_find_key()` matches signed-info issuer IDs to embedded certs. `pkcs7_verify_sig_chain()` verifies embedded certificate chains and detects loops/blacklisting. `pkcs7_verify_one()` verifies one signer. `pkcs7_verify()` enforces usage policy and iterates signers. `pkcs7_supply_detached_data()` attaches caller-owned data to a parsed detached signature.

Control flow: verification first validates the requested usage's expected content type/authattrs policy. For each signer, it digests content, verifies messageDigest authattr when present, re-digests authattrs as a SET for signature verification, locates the signer certificate, checks signing time against certificate validity if available, verifies the signed info signature, and verifies embedded chain signatures as far as possible.

State and persistence: verification mutates `sig->m`, `sig->m_size`, `sig->m_free`, signer pointers, certificate `seen`, `signer`, `blacklisted`, and signed-info flags. Detached data is only borrowed; callers must keep it alive.

Dependencies and integration points: depends on shash algorithms, hash-name mapping, public-key verification, X.509 certificate structures, ASN.1 tag constants, and higher-level module/firmware/kexec/BPF verification callers.

Risks: authenticated attribute canonicalization is subtle; the code mutates the first tag byte from context-specific to SET before hashing. Usage policy differences can reject valid-looking messages for the wrong context. Missing hash/signature algorithms produce `-ENOPKG`, which must not be confused with trust failure. Detached data lifetime is external.

Test signals: attached/detached signatures, authattrs digest mismatch, signing time outside certificate validity, blacklisted certificates, unsupported hash algorithms, ML-DSA raw-data behavior, module versus firmware versus kexec usage policy, and certificate-chain loops.
