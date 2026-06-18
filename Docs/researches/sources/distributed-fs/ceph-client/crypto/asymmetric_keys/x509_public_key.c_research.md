# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_public_key.c

Purpose: converts parsed X.509 certificates into asymmetric public-key payloads and prepares certificate signatures for verification.

Important APIs/types/functions: `x509_get_sig_params()` duplicates the raw signature, computes the certificate TBS digest or assigns raw TBS data for algorithms that take data, and checks the TBS SHA-256 against the blacklist. `x509_check_for_self_signed()` compares subject/issuer and AKID/SKID/issuer IDs, then verifies self-signatures when crypto is available. `x509_key_preparse()` parses a certificate, rejects blacklisted certs, creates a key description, builds key IDs, and transfers public key/signature state into the asymmetric key payload. `x509_key_parser` registers the parser.

Control flow: asymmetric key preparse invokes this parser for X.509 blobs. Parsed certificates become `public_key_subtype` keys with `X509` id type, generated description, three possible key IDs, crypto payload, and auth signature payload. Unsupported certificate signatures can still allow key instantiation with no auth payload unless blacklisted.

State and persistence: key payloads take ownership of `cert->pub`, `cert->sig`, `cert->id`, and `cert->skid`; parser cleanup owns anything not transferred. Descriptions persist with keys. The computed SHA-256 TBS hash is only used for blacklist checks.

Dependencies and integration points: depends on shash allocation, blacklist APIs, public-key subtype, asymmetric parser registry, and X.509 parser internals.

Risks: blacklist handling intentionally sets `cert->blacklisted` but continues enough cleanup to avoid leaks. Algorithms without available hash support mark `unsupported_sig`, affecting trust restrictions. Description generation uses subject plus SKID or serial and must allocate enough hex space.

Test signals: valid X.509 key add, blacklisted TBS rejection, unsupported hash algorithm, self-signed verification success/failure, SKID versus serial description generation, and key ID lookup after import.
