# sources/distributed-fs/ceph-client/tools/certs/print-cert-tbs-hash.sh

Purpose: Computes the Linux blacklist key description for a certificate by hashing the TBSCertificate region with the certificate signature hash algorithm and printing `tbs:<hash>` without a newline.

Important APIs, types, and functions: Shell variables capture certificate path, ASN.1 offset/length/digest, and selected digest command. Uses `openssl x509`, `openssl asn1parse`, `openssl list -digest-commands`, `dd`, `openssl dgst`, `sed`, and `awk`.

Control flow: Validates one file argument, converts DER or PEM input to normalized PEM, parses line 2 for TBSCertificate offset/length and line 7 for signature digest OID name, matches the digest against OpenSSL digest commands, converts the cert to DER, extracts the TBS byte range with `dd`, hashes it, and prints the prefixed digest.

State and persistence: Read-only; intended output is redirected by the caller for later PKCS#7 signing and keyctl loading.

Dependencies and integration points: Integrates with Linux asymmetric key blacklist workflow and references kernel X.509 parser behavior. Requires OpenSSL command-line tools and POSIX shell utilities.

Risks: ASN.1 parsing assumes specific OpenSSL output line positions. `dd count` is set to `OFFSET + length` while also using `skip=OFFSET`, so this mirrors current script behavior but is a subtle area to verify against expected byte counts. Digest matching depends on OpenSSL command names containing the signature digest text.

Test signals: Run on PEM and DER certificates with SHA-256/SHA-1 signatures, invalid files, and compare against kernel-generated blacklist descriptions where available.
