# Group Research: group_1397_openbsd_src_sources_os_bsd_openbsd_src_sbin_unwind_libunbound_valid_d077fb23a3c0

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/openbsd-src`, which is included in subset A. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.h

This header declares the validator’s NSEC denial-of-existence interface. It is part of libunbound’s DNSSEC validation layer inside OpenBSD `unwind`.

It exposes helpers for proving DS absence, checking NSEC type bitmaps, proving NODATA, NXDOMAIN/name errors, positive wildcard correctness, wildcard absence, closest-encloser derivation, and insecure delegation detection. The API works with `ub_packed_rrset_key`, `query_info`, `reply_info`, validator/module environments, and DNSSEC key entries.

Key contracts:
- `val_nsec_prove_nodata_dsreply()` validates NODATA responses to DS queries and can return secure absence, insecure non-delegation, bogus validation failure, or unchecked lack of proof.
- `nsecbitmap_has_type_rdata()` and `nsec_has_type()` provide type bitmap inspection.
- `nsec_proves_nodata()`, `val_nsec_proves_name_error()`, `val_nsec_proves_positive_wildcard()`, and `val_nsec_proves_no_wc()` encode the major NSEC proof forms.
- `nsec_closest_encloser()` returns closest-encloser data after name-error proof.
- `val_nsec_proves_insecuredelegation()` identifies unsigned delegation proofs.

Important dependencies:
- Uses packed RRset storage and LDNS RR type constants.
- Reason strings and EDE codes are threaded through validation failures.
- The header is consumed by NSEC3 code for bitmap handling and by validator denial logic.

Research notes:
- This is a pure declaration file with detailed proof semantics in comments.
- It establishes the NSEC counterpart to `val_nsec3.h`; NSEC3 implementation reuses `nsecbitmap_has_type_rdata()` for type bitmap interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.c

This file implements NSEC3 denial-of-existence proof logic for DNSSEC validation. It handles NSEC3 parsing, parameter filtering, hash calculation and caching, closest-encloser proofs, wildcard nonexistence, NODATA, NXDOMAIN, DS no-data, and combined NXDOMAIN-or-NODATA validation.

Core structures:
- `ce_response` stores closest-encloser proof state: closest encloser name, matching NSEC3, and next-closer covering NSEC3.
- `nsec3_filter` restricts candidate NSEC3 records to the relevant zone, class, known algorithm, and known flags.
- `nsec3_cached_hash` stores name hash outputs, base32 labels, and cache keys.
- `nsec3_cache_table` owns a regional rbtree cache for repeated hash lookups.

Parsing and filtering:
- `nsec3_get_params()`, `nsec3_get_nextowner()`, `nsec3_has_type()`, and `nsec3_has_optout()` parse individual NSEC3 RDATA fields with length checks.
- `filter_init()`, `filter_first()`, and `filter_next()` select usable NSEC3 RRs for the best matching zone.
- Unknown algorithms or unknown flags are ignored by the iterator.
- `param_set_same()` rejects mixed NSEC3 chains with mismatched algorithm, iteration count, or salt.

Hashing:
- `nsec3_get_hashed()` computes NSEC3 iterative hashes.
- `nsec3_hash_name()` caches computed hashes in an rbtree keyed by name plus NSEC3 parameters.
- `nsec3_hash_cmp()` compares cache keys using dname, algorithm, iteration count, and salt.
- `nsec3_hash_to_b32()` and `nsec3_get_nextowner_b32()` construct base32 owner names.

Proof mechanics:
- `find_matching_nsec3()` finds an NSEC3 whose owner matches a hashed name.
- `find_covering_nsec3()` finds an NSEC3 span covering a hashed name.
- `nsec3_covers()` implements normal and wraparound hash interval coverage.
- `nsec3_find_closest_encloser()` walks from qname toward zone apex until a matching NSEC3 is found.
- `nsec3_prove_closest_encloser()` verifies the closest-encloser candidate and next-closer coverage, rejecting DNAME and invalid delegation cases.

Public proof entry points:
- `nsec3_prove_nameerror()` proves NXDOMAIN by proving closest encloser, next closer nonexistence, and wildcard nonexistence.
- `nsec3_prove_nodata()` proves NODATA using matching NSEC3, wildcard NODATA, and opt-out cases.
- `nsec3_prove_wildcard()` proves positive wildcard applicability by covering the next closer.
- `nsec3_prove_nods()` verifies DS absence, including normal NODATA and opt-out DS NODATA.
- `nsec3_prove_nxornodata()` tries NXDOMAIN first, then NODATA while preserving the hash cache.

Security behavior:
- Uses `MAX_NSEC3_CALCULATIONS` to limit expensive hashing and returns `sec_status_unchecked` when proof should be suspended/retried.
- Treats all attempted hash calculations failing as bogus via `MAX_NSEC3_ERRORS`.
- Enforces validator-configured maximum NSEC3 iterations based on DNSKEY size; excessive iterations return insecure.
- Opt-out spans generally produce insecure results rather than secure AD-valid answers.
- DS proofs require NSEC3 RRsets to be cryptographically secure first via `list_is_secure()`.

Important dependencies:
- `val_secalgo.c` for NSEC3 SHA-1 hashing.
- `val_nsec.h` for NSEC/NSEC3 bitmap type checks.
- validator key entries for key size and key validity.
- regional allocator and scratch buffer for temporary proof state.

Research notes:
- The implementation is careful about malformed RDATA and mixed-chain proofs.
- The hash cache is central because several proof paths repeatedly hash qname, ancestors, next-closer names, and wildcard names.
- The code distinguishes bogus proof failure, insecure opt-out/delegation behavior, and unchecked computational deferral.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.h

This header defines the NSEC3 validator API and supporting cache structures. It documents NSEC3 and NSEC3PARAM wire layout and declares proof functions used by the DNSSEC validator.

Key constants:
- `NSEC3_OPTOUT` is the opt-out flag.
- `NSEC3_UNKNOWN_FLAGS` masks unsupported flags.
- `NSEC3_HASH_SHA1` is the supported NSEC3 hash algorithm.
- `MAX_NSEC3_CALCULATIONS` limits per-pass NSEC3 hash work.

Public proof API:
- `nsec3_prove_nameerror()` proves NXDOMAIN with closest-encloser, next-closer, and wildcard proofs.
- `nsec3_prove_nodata()` proves NOERROR/NODATA across normal, wildcard, ENT, and opt-in/opt-out DS cases.
- `nsec3_prove_wildcard()` proves a positive wildcard response was appropriate.
- `nsec3_prove_nods()` proves no DS or insecure opt-out DS absence.
- `nsec3_prove_nxornodata()` tries to prove either NXDOMAIN or NODATA and reports which proof succeeded.

Hash/cache API:
- `struct nsec3_cache_table` stores a regional rbtree pointer and its allocation region.
- `struct nsec3_cached_hash` records NSEC3 parameters, dname, raw hash, and base32 label.
- `nsec3_cache_table_init()` initializes the cache.
- `nsec3_hash_cmp()` is the rbtree comparator.
- `nsec3_hash_name()` returns cached or newly computed hashes.

Parsing helpers:
- `nsec3_get_nextowner_b32()` and `nsec3_hash_to_b32()` construct base32 owner names.
- `nsec3_get_params()` returns algorithm, iterations, and salt.
- `nsec3_get_hashed()` computes raw NSEC3 hashes.
- `nsec3_has_type()`, `nsec3_has_optout()`, and `nsec3_get_nextowner()` inspect individual NSEC3 RRs.
- `nsec3_covers()` tests whether an NSEC3 RR covers a hash.

Research notes:
- The header explicitly exposes some internal mechanics for unit testing.
- Return status semantics are important: secure, bogus, insecure, unchecked, and indeterminate carry different validator meanings.
- The cache structure stores pointers into regional allocation, so callers must reinitialize after region cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_nsec3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.c

This file provides the crypto-backend adapter for DNSSEC validation. It maps DNSSEC/NSEC3/DS algorithms to OpenSSL, NSS, or Nettle calls depending on compile-time configuration.

Shared validator-facing API:
- `nsec3_hash_algo_size_supported()` reports supported NSEC3 digest length.
- `secalgo_nsec3_hash()` hashes NSEC3 input, currently SHA-1.
- `secalgo_hash_sha256()` computes SHA-256.
- `secalgo_hash_create_sha384()`, `secalgo_hash_create_sha512()`, `secalgo_hash_update()`, `secalgo_hash_final()`, and `secalgo_hash_delete()` provide streaming hash support.
- `ds_digest_size_supported()` and `secalgo_ds_digest()` support DS digest calculation.
- `dnskey_algo_id_is_supported()` declares supported DNSKEY algorithms.
- `verify_canonrrset()` verifies canonicalized RRset bytes against a DNSKEY public key and RRSIG signature block.

OpenSSL path:
- Supports SHA-1, SHA-256, SHA-384, SHA-512, optional GOST, DSA, RSA, ECDSA, Ed25519, and Ed448 depending on macros.
- Converts DSA signatures to DER via `setup_dsa_sig()`.
- Converts raw ECDSA DNSSEC signatures to ASN.1 DER via `setup_ecdsa_sig()`.
- Builds EVP public keys in `setup_key_digest()`.
- Uses `EVP_DigestVerify*` or older `EVP_VerifyFinal` APIs.
- Handles OpenSSL 3 digest refusal as `sec_status_indeterminate` when detectable.

NSS path:
- Implements hash support through NSS `HASH_*` APIs.
- Builds NSS public key objects for RSA, DSA, and ECDSA.
- Adds ASN hash prefixes for RSA verification where needed.
- Uses `PK11_Verify()` and maps bad signatures to bogus, missing modules to unchecked.

Nettle path:
- Implements direct digest helpers for SHA-1/SHA-256/SHA-384/SHA-512.
- Parses and verifies DSA, RSA, ECDSA, and Ed25519 signatures with Nettle primitives.
- Performs explicit DNSSEC wire key parsing for RSA exponent/modulus and DSA parameters.
- Returns human-readable reason strings for signature and key parsing failures.

Security behavior:
- RSAMD5 is rejected as deprecated.
- SHA-1 and DSA can be faked for unit testing via `fake_sha1` and `fake_dsa`.
- Algorithm support is compile-time gated and may also depend on FIPS mode or runtime provider availability.
- Signature mismatch maps to bogus; allocation or crypto-library operational failures generally map to unchecked or indeterminate.

Research notes:
- This file does not canonicalize RRsets; it assumes `val_sigcrypt.c` already built the canonical verification buffer.
- The file’s complexity is mostly portability glue across three crypto stacks.
- OpenSSL, NSS, and Nettle all expose the same validator-facing function names, so only one backend block compiles.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.h

This header declares the validator’s cryptographic algorithm abstraction. It hides OpenSSL/NSS/Nettle details behind stable DNSSEC validation functions.

Declared capabilities:
- NSEC3 hash support and one-shot hashing.
- SHA-256 one-shot hashing.
- Streaming SHA-384 and SHA-512 hash contexts.
- DS digest support and digest size lookup.
- DNSKEY algorithm support checks.
- Canonical RRset signature verification through `verify_canonrrset()`.

Key data type:
- `struct secalgo_hash` is opaque to callers and implemented per backend in `val_secalgo.c`.

Important function contracts:
- `nsec3_hash_algo_size_supported()` returns 0 for unsupported NSEC3 hash algorithms.
- `secalgo_nsec3_hash()` and `secalgo_ds_digest()` return false on unsupported algorithms or backend failure.
- `dnskey_algo_id_is_supported()` is used before expensive verification attempts.
- `verify_canonrrset()` returns secure, bogus, unchecked, or indeterminate depending on signature result and backend failure mode.

Research notes:
- This is the narrow crypto boundary used by both NSEC3 hashing and RRSIG verification.
- The header intentionally works on raw buffers, leaving DNS wire parsing and canonicalization to other validator files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_secalgo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.c

This file bridges DNSSEC wire-format RRsets to cryptographic verification. It extracts DNSKEY/DS/RRSIG fields, validates signature metadata, canonicalizes RRsets, enforces downgrade-protection algorithm requirements, and calls `verify_canonrrset()`.

RRset and key access:
- Local helpers read RR counts, RRSIG counts, RRSIG keytags, RRSIG algorithms, and RDATA pointers.
- `dnskey_get_flags()`, `dnskey_get_algo()`, `dnskey_calc_keytag()`, `ds_get_keytag()`, `ds_get_key_algo()`, and `ds_get_digest_algo()` expose DNSKEY/DS metadata.
- `dnskey_algo_is_supported()`, `dnskey_size_is_supported()`, and `dnskeyset_size_is_supported()` enforce algorithm and optional RSA key-size policy.
- `ds_digest_match_dnskey()` computes a DS digest from DNSKEY owner name plus DNSKEY RDATA and compares it to the DS record.

Algorithm needs tracking:
- `struct algo_needs` tracks which signing algorithms still require successful validation.
- `algo_needs_init_dnskey_add()`, `algo_needs_init_ds()`, and `algo_needs_init_list()` initialize requirements.
- `algo_needs_set_secure()`, `algo_needs_set_bogus()`, `algo_needs_missing()`, and `algo_needs_reason()` implement downgrade-protection reporting.

Signature verification flow:
- `dnskeyset_verify_rrset()` verifies an RRset against a DNSKEY set, optionally requiring all signaled algorithms to validate.
- `dnskey_verify_rrset()` verifies an RRset against one specific DNSKEY.
- `dnskey_verify_rrset_sig()` verifies one RRset/RRSIG/DNSKEY combination after all metadata checks.
- `MAX_VALIDATE_RRSIGS` limits the number of RRSIG validation attempts.

Canonicalization:
- `canonical_compare_byfield()` and `canonical_compare()` sort RR RDATA in DNSSEC canonical order, lowercasing embedded domain names where required by RR type.
- `canonical_tree_compare()` and `canonical_sort()` build rbtree ordering and remove duplicates.
- `insert_can_owner()` handles wildcard-expanded owner names according to RRSIG label count.
- `canonicalize_rdata()` lowercases name fields for RR types requiring canonical name treatment.
- `rrset_canonical()` builds the exact signature input buffer: RRSIG covered fields plus sorted canonical RRs.
- `rrset_canonicalize_to_buffer()` canonicalizes an auth-zone RRset without an RRSIG context.
- `rrset_canonical_equal()` compares two RRsets after canonical sorting.

RRSIG checks:
- Validates signer name format, signer/key name match, covered type, algorithm, keytag, DNSKEY protocol, ZSK flag, revoked-key constraints, and label count.
- `check_dates()` verifies inception/expiration with RFC 1982 serial arithmetic and configurable clock skew.
- `adjust_ttl()` clamps verified RRset TTL to original RRSIG TTL and signature expiration.

Security behavior:
- Unsupported DNSKEY algorithms can produce insecure or indeterminate depending on context.
- Signature mismatch is bogus; missing matching key/signature is bogus with EDE reason.
- Too many signature validations is bogus.
- Authority-section NSEC owner names may be rewritten to canonical owner after wildcard handling to avoid synthesized NSEC misuse in denial proofs.

Research notes:
- This is the main correctness-sensitive canonicalization layer.
- It depends on `val_secalgo.c` only after all DNSSEC metadata and canonical buffer construction have succeeded.
- The code is defensive about malformed RRSIGs, short DNSKEYs, off-tree signers, wrong covered types, revoked keys, and label-count abuse.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.h

This header declares signature verification, DS/DNSKEY matching, DNSKEY metadata extraction, canonical RRset comparison, and algorithm downgrade-protection helpers.

Key structures:
- `ALGO_NEEDS_MAX` is 256, matching 8-bit DNSKEY algorithm identifiers.
- `struct algo_needs` stores per-algorithm states: not needed, needed, or bogus, plus outstanding count.

Algorithm tracking API:
- `algo_needs_init_dnskey_add()` adds DNSKEY algorithms to a requirement set.
- `algo_needs_init_list()` initializes from a signaled algorithm list.
- `algo_needs_init_ds()` initializes from DS records filtered by preferred DS digest algorithm.
- `algo_needs_set_secure()`, `algo_needs_set_bogus()`, `algo_needs_num_missing()`, `algo_needs_missing()`, and `algo_needs_reason()` support downgrade-resistant validation reporting.

DS/DNSKEY helpers:
- `ds_digest_match_dnskey()` checks DS digest against DNSKEY.
- `dnskey_calc_keytag()`, `ds_get_keytag()`, `dnskey_get_algo()`, `dnskey_get_flags()`, `ds_get_key_algo()`, and `ds_get_digest_algo()` parse key metadata.
- `dnskey_algo_is_supported()`, `dnskey_size_is_supported()`, `dnskeyset_size_is_supported()`, `ds_digest_algo_is_supported()`, and `ds_key_algo_is_supported()` expose support policy.

Signature verification API:
- `dnskeyset_verify_rrset()` verifies an RRset against a DNSKEY set.
- `dnskey_verify_rrset()` verifies against a single DNSKEY from a set.
- `dnskey_verify_rrset_sig()` verifies one signature with one DNSKEY and can reuse canonical sort/canonical buffer state.

Canonical RRset API:
- `canonical_tree_compare()` provides rbtree canonical ordering.
- `rrset_canonical_equal()` compares RRsets canonically.
- `rrset_canonicalize_to_buffer()` serializes an RRset into canonical wire form.

Research notes:
- This header is the primary interface between high-level validator logic and the lower crypto adapter.
- It includes EDE-aware failure reporting and packet section context because validation behavior differs for answer/authority processing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_sigcrypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.c

This file provides high-level validator utility logic around response classification, signer discovery, RRset validation cache updates, DS/DNSKEY trust-chain validation, wildcard/CNAME/DNAME handling, message cleanup, and cached DS lookup.

Response classification:
- `val_classify_response()` classifies replies as name error, NODATA, referral, positive, CNAME, CNAME-no-answer, ANY, or unknown.
- It handles non-recursive referrals, root referral form, CNAME chains ending in NXDOMAIN, DNAME query special cases, and ANY responses.
- `val_classification_to_string()` formats classifications for logging.

Signer discovery:
- `rrsig_get_signer()` parses signer names from RRSIG RDATA.
- `val_find_rrset_signer()` returns the first RRSIG signer.
- `val_find_best_signer()` chooses the closest signer for CNAME-no-answer authority proofs.
- `cname_under_previous_dname()` detects synthesized CNAMEs caused by previous DNAMEs.
- `val_find_signer()` selects appropriate signer names depending on response subtype.

RRset verification:
- `val_verify_rrset()` checks cached security status, invokes `dnskeyset_verify_rrset()`, updates RRset security/trust, adjusts bogus TTLs, increments bogus counters, and stores status in the RRset cache.
- `val_verify_rrset_entry()` creates a temporary DNSKEY RRset view from a key entry and verifies an RRset against it.

DS/DNSKEY validation:
- `verify_dnskeys_with_ds_rr()` matches one DS against candidate DNSKEYs by algorithm, keytag, digest, key size, and DNSKEY self-signature.
- `val_favorite_ds_algo()` chooses the highest-numbered supported DS digest algorithm.
- `val_verify_DNSKEY_with_DS()` validates DNSKEY RRsets through DS RRsets, including downgrade protection with `algo_needs`.
- `val_verify_new_DNSKEYs()` creates good, null, or bad key entries from DS-based validation results.
- `val_verify_DNSKEY_with_TA()` validates DNSKEY RRsets against trust-anchor DS and/or DNSKEY RRsets.
- `val_verify_new_DNSKEYs_with_ta()` creates key entries from trust-anchor validation results.
- `val_dsset_isusable()` checks whether a DS set has at least one supported digest/key algorithm pair.

Wildcard and CNAME/DNAME handling:
- `val_rrset_wildcard()` detects whether an RRset was wildcard synthesized by comparing RRSIG label counts.
- `val_chase_cname()` advances a query-info chase through matching CNAME records.
- `derive_cname_from_dname()` constructs the expected CNAME target from a DNAME owner and target.

Reply construction and cleanup:
- `val_fill_reply()` builds a chase reply containing RRsets matching a name or signer, with special handling for DNAME-generated unsigned CNAMEs.
- `val_reply_remove_auth()` removes one authority-section RRset.
- `val_check_nonsecure()` marks a message bogus if required authority data is not secure, but may remove nonessential insecure NS/additional data for lenient minimal responses.
- `val_mark_indeterminate()` marks unchecked RRsets indeterminate when no trust anchor applies.
- `val_mark_insecure()` marks unchecked RRsets insecure below an insecure key name.
- `val_next_unchecked()` finds the next unchecked RRset after a given index.

Other helpers:
- `val_blacklist()` merges or prepends origin socket lists into a validator blacklist.
- `val_has_signed_nsecs()` checks whether authority NSEC/NSEC3 records have signatures and supplies a failure reason.
- `val_find_DS()` looks for DS data in the RRset cache first, then negative cache, returning an internal DNS message.

Security behavior:
- DS matching limits repeated digest mismatches per DS with `MAX_DS_MATCH_FAILURES`.
- Unsupported DS/DNSKEY algorithms can lead to insecure status when no useful supported chain exists.
- Bogus RRsets have TTLs clamped to validator bogus TTL and are counted under lock.
- Trust-anchor mismatch by owner name is immediately bogus.
- Additional-section cleanup can remove unsigned data without invalidating the whole message when configured.

Research notes:
- This file ties together `val_sigcrypt`, key-entry creation, anchors, caches, and negative proof lookup.
- It is high-level validation glue rather than low-level crypto or NSEC proof code.
- The response classification and signer-finding paths are central for deciding which key name to fetch and which RRsets to validate next.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.c -->