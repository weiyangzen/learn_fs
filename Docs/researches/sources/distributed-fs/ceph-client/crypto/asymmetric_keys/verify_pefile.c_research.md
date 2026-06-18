# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.c

Purpose: verifies Authenticode-style signatures on PE binaries by parsing the PE headers, extracting the embedded PKCS#7 signature, validating the PKCS#7 trust chain, and comparing the signed Microsoft code-signing digest with a locally computed PE digest.

Important APIs/types/functions: `pefile_parse_binary()` validates DOS/PE/optional headers, records checksum and certificate-directory offsets, and locates sections. `pefile_strip_sig_wrapper()` validates the `WIN_CERTIFICATE` wrapper and trims padding. `pefile_compare_shdrs()` canonicalizes section order. `pefile_digest_pe_contents()` hashes the PE image while excluding checksum and certificate directory. `pefile_digest_pe()` allocates the selected hash and compares digests. `verify_pefile_signature()` is the exported top-level verifier.

Control flow: verification parses PE metadata, strips the certificate wrapper, calls `verify_pkcs7_signature()` over the PKCS#7 signature with `mscode_parse()` as content callback, then computes the PE digest named by the signed content and compares it to the digest extracted from the PKCS#7 authenticated content.

State and persistence: all state is in stack `struct pefile_context`, plus a heap-duplicated expected digest freed before return. Section pointers borrow from the PE buffer. No persistent state is written.

Dependencies and integration points: depends on `linux/pe.h`, shash algorithms, PKCS#7 verification, Microsoft code-signing ASN.1 parser, and trusted keyrings supplied by callers such as kexec PE verification.

Risks: PE bounds checking is security-critical for untrusted binaries. Digest canonicalization must exactly match Authenticode, including omitted checksum/cert data and section sorting. The tail hashing path must avoid underflow around certificate table padding. Indefinite-length PKCS#7 acceptance leaves length validation to the ASN.1 layer.

Test signals: signed and unsigned PE images, PE32 and PE32+ headers, malformed header offsets, wrapper length/padding variants, unsupported cert types, section ordering edge cases, digest mismatch, unsupported hash algorithm, and trust keyring failures.
