# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/mscode_parser.c

Purpose: parses Microsoft Individual Code Signing authenticated content embedded in Authenticode PKCS#7 signatures and extracts the PE image digest algorithm and digest.

Important APIs/types/functions: `mscode_parse()` adjusts the content pointer to include the ASN.1 header and invokes `asn1_ber_decoder()` with `mscode_decoder`. `mscode_note_content_type()` validates that the content type is a PE image data OID, with a compatibility allowance for a historical `pesign` bug. `mscode_note_digest_algo()` maps supported OIDs to crypto hash names. `mscode_note_digest()` duplicates the signed digest into `struct pefile_context`.

Control flow: `verify_pefile_signature()` passes `mscode_parse()` as the PKCS#7 content callback. During ASN.1 decode, OID callbacks validate content and choose the hash algorithm, then the digest callback stores the expected PE digest for later comparison against a locally computed digest.

State and persistence: state is stored only in the caller-provided `struct pefile_context`: `digest_algo`, `digest`, and `digest_len`. The digest allocation is freed by PE verification cleanup.

Dependencies and integration points: depends on generated `mscode.asn1.h`, OID registry helpers, PKCS#7 callback conventions, and `verify_pefile.h`.

Risks: accepting the historical alternate OID is intentional but broadens accepted input. Digest OID support must match available crypto hash algorithms. The pointer adjustment by `asn1hdrlen` assumes the PKCS#7 callback contract remains stable.

Test signals: Authenticode signatures with sha1/sha2/sha3 digests, unknown OID rejection, alternate `OID_msIndividualSPKeyPurpose` acceptance, malformed ASN.1, and digest allocation failure.
