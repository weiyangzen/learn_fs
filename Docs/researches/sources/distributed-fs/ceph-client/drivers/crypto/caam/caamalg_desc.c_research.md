# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.c

## Purpose

`caamalg_desc.c` is the shared descriptor construction library for the Freescale/NXP CAAM crypto driver. It does not execute requests directly. Instead, it emits CAAM descriptor words into caller-owned `u32` buffers for AEAD, GCM/IPsec GCM/GMAC, ChaCha20-Poly1305, skcipher, XTS, protected-blob key decapsulation, and one protected-key skcipher job descriptor. These descriptors are later installed into job-ring or Queue Interface driver contexts by higher-level CAAM algorithm files such as `caamalg_qi.c`.

The file is hardware-facing glue: most logic is sequencing CAAM class 1 cipher engines, class 2 authentication engines, descriptor math registers, variable-length FIFO loads/stores, key loading, IV/counter layout, and erratum workarounds. Exported functions are small public construction entry points, while static helpers factor common AEAD/skcipher descriptor fragments.

## Important APIs and functions

- `aead_append_src_dst()` appends the common AEAD payload store/load pair: write message data to output and load variable-length data to class 1/class 2 using the requested FIFO message type.
- `append_dec_op1()` emits class 1 decrypt operations. For AES descriptors that may be shared it conditionally emits a DK-bit variant when the descriptor is already shared; non-AES algorithms use a normal init-final decrypt operation.
- `cnstr_shdsc_aead_null_encap()` and `cnstr_shdsc_aead_null_decap()` build null-encryption ESP-style HMAC descriptors, including split-key or DKP auth key handling, variable-length assoc+payload movement, descriptor self-patching for older hardware without `MOVE_LEN`, and ICV write/read.
- `init_sh_desc_key_aead()` initializes shared AEAD descriptors with saved context, loads auth and cipher keys, handles SEC era differences for DKP versus precomputed split keys, and preloads RFC3686 nonces into class 1 context.
- `cnstr_shdsc_aead_encap()`, `cnstr_shdsc_aead_decap()`, and `cnstr_shdsc_aead_givencap()` build generic authenc descriptors for encryption, decryption, and generated-IV encryption. They support QI-specific assoclen/IV input format, RFC3686 counter setup, generated chained IV output, and class 1/class 2 sequencing.
- `cnstr_shdsc_gcm_encap()` and `cnstr_shdsc_gcm_decap()` build generic AES-GCM descriptors with zero-associated-data and zero-payload branches, QI IV loading, tag write or verification, and optional inline/DMA key forms.
- `cnstr_shdsc_rfc4106_encap()` and `cnstr_shdsc_rfc4106_decap()` build IPsec ESP GCM descriptors where salt is appended to key material and IV is part of AAD. They include a workaround for CAAM erratum A-005473 around simultaneous sequence FIFO skips.
- `cnstr_shdsc_rfc4543_encap()` and `cnstr_shdsc_rfc4543_decap()` build IPsec GMAC descriptors that authenticate assoc+payload while forwarding payload unchanged through OFIFO, using descriptor self-patching where `MOVE_LEN` is unavailable.
- `cnstr_shdsc_chachapoly()` builds generic RFC7539 and IPsec RFC7634 ChaCha20-Poly1305 descriptors. It loads ChaCha and Poly operations, optionally installs IPsec salt, routes associated data through both class alignment blocks, emits metadata IV for IPsec output, and either writes or verifies the tag.
- `skcipher_append_src_dst()` is the common skcipher variable-length class 1 load/store sequence.
- `cnstr_desc_skcipher_enc_dec()` builds a complete job descriptor for protected-key skcipher operations using external source/destination pointers, protected key DMA address, optional IV load/store, and class 1 operation.
- `cnstr_desc_protected_blob_decap()` builds a job descriptor that converts a CAAM black blob key into a protected key, using `KEYMOD` and optionally jumping to a next descriptor.
- `cnstr_shdsc_skcipher_encap()` and `cnstr_shdsc_skcipher_decap()` build shared skcipher descriptors for CBC/CTR/DES/3DES/ChaCha20-style algorithms, including RFC3686 nonce and counter layout, IV load/store, and ChaCha finalize behavior.
- `cnstr_shdsc_xts_skcipher_encap()` and `cnstr_shdsc_xts_skcipher_decap()` build XTS AES descriptors, install a large sector size to effectively disable CAAM sector segmentation for Linux crypto API/dm-crypt usage, load the two halves of the 16-byte tweak into CAAM context offsets, and store the resulting IV/tweak state.

All construction entry points are exported with `EXPORT_SYMBOL`, so this file is an internal module API for other CAAM algorithm frontends.

## Control flow

Most descriptor constructors follow the same high-level pattern:

1. Initialize a job or shared descriptor with `init_job_desc()` or `init_sh_desc()`, often using `HDR_SHARE_SERIAL` and sometimes `HDR_SAVECTX`.
2. Emit a "skip if already shared" jump around key-loading commands. Shared descriptors are expected to avoid reloading keys after hardware context sharing has already materialized them.
3. Select inline versus DMA key commands based on `struct alginfo` fields supplied by the caller. AEAD auth descriptors use era-specific split key versus DKP behavior.
4. Load QI-specific leading metadata when `is_qi` is true. For AEAD/GCM this usually means reading a 4-byte assoclen into math register 3, waiting for descriptor engine pipeline conditions to clear, and loading IV bytes from the input frame rather than from a job descriptor pointer.
5. Program CAAM math registers such as `VARSEQINLEN`, `VARSEQOUTLEN`, `SEQINLEN`, `SEQOUTLEN`, `REG0`, `REG2`, and `REG3` to drive variable-length FIFO movement.
6. Emit class operations (`append_operation`) for class 1 cipher and class 2 authentication engines in the required order.
7. Emit sequence FIFO loads/stores for associated data, payload, IV, and tag/ICV.
8. Backpatch local jumps and move targets with `set_jump_tgt_here()` or `set_move_tgt_here()`.
9. Dump the descriptor with `print_hex_dump_debug()` for debug builds.

The AEAD authenc path authenticates assoc data before payload, then encrypts/decrypts class 1 data while class 2 writes or verifies the ICV. GCM/RFC4106/RFC4543 paths are class 1 GCM-based and have extra zero-length branches to keep CAAM operation semantics valid when assoc or payload lengths are zero. ChaCha-Poly uses both class 1 and class 2 AEAD operations and an NFIFO path to feed associated data to both engines while forwarding it to output as needed.

## State and persistence behavior

This file maintains no global mutable runtime state. Its persistent effects are the descriptor words written into the caller-provided `desc` buffers and, for job descriptors, embedded DMA addresses and immediate key modifier data. It relies on callers to allocate buffers large enough for the advertised descriptor length macros, preserve key memory for inline immediate emission until descriptor construction finishes, DMA-map any pointer-based key material, and install/update descriptors in CAAM driver contexts.

Within a generated descriptor, CAAM hardware state is deliberately manipulated: class 1/class 2 contexts can be saved across shared descriptor invocations, keys may be loaded once and reused under descriptor sharing, context registers hold IVs/nonces/counters/tweaks, and descriptor math registers hold assoc/payload lengths. These are hardware execution states, not C-side persistent state.

## Dependencies and integration points

The implementation depends heavily on CAAM descriptor builder APIs and hardware constants from `desc_constr.h`, compatibility/types from `compat.h`, and blob protocol constants from `<soc/fsl/caam-blob.h>`. It consumes `struct alginfo` fields such as `algtype`, key virtual/DMA addresses, key lengths, `key_inline`, protected key addresses, `plain_keylen`, and `key_cmd_opt`.

Primary consumers include QI and non-QI CAAM algorithm frontends. In this subset, `caamalg_qi.c` calls the AEAD, GCM, RFC4106, RFC4543, skcipher, and XTS constructors when keys or auth sizes change and then installs the descriptors into QI driver contexts. The header also exposes protected-blob helpers used by protected-key flows elsewhere in the CAAM driver.

The `is_qi` parameter is an important integration boundary: QI descriptors expect a leading assoclen entry and often IV data in the input frame's scatter/gather layout, while non-QI descriptors rely on different job descriptor overrides such as `DPOVRD`. SEC era is another boundary: era < 6 paths require precomputed split auth keys, while newer hardware can use descriptor key protocol (`append_proto_dkp`).

## Risks and edge cases

- Descriptor length accounting is critical. Callers must reserve enough words for selected options such as QI, RFC3686 nonce/counter setup, generated IV, and inline keys.
- Length math depends on CAAM register conventions (`REG0` as zero-sized adjust, `REG3` as assoclen, `SEQINLEN`/`SEQOUTLEN` semantics). A mismatch between caller frame layout and descriptor math can corrupt output, drop authentication data, or misverify tags.
- Several paths self-patch descriptor buffer move lengths to work around hardware revisions without `MOVE_LEN`. The required instruction spacing is subtle and easy to regress.
- RFC3686 and IPsec GCM/GMAC key layouts intentionally treat trailing bytes as nonce/salt. Incorrect `cdata->keylen` or `key_virt` setup by callers would make descriptors read wrong nonce/salt bytes.
- GCM zero-associated-data and zero-payload jumps are correctness-sensitive; off-by-one jump distances would affect empty-message authentication.
- The RFC4106 erratum A-005473 workaround should be preserved when refactoring sequence FIFO skip/store order.
- `append_dec_op1()` has AES-specific DK handling. Using it with wrong `algtype` or wrong context offset selection could produce decrypt operations incompatible with shared AES contexts.
- Debug dumps can expose descriptor contents and possibly inline key material in debug logs if dynamic debug is enabled.
- Protected blob descriptors embed protocol options derived from `key_cmd_opt`; EKT handling and protected key lengths must stay aligned with blob/key management code.

## Test signals

Useful validation signals include kernel crypto API self-tests for every registered CAAM algorithm name, AF_ALG/tcrypt tests for CBC/CTR/RFC3686/XTS and authenc combinations, IPsec ESP tests for RFC4106 and RFC4543 including zero-length payload and AAD-only cases, generated-IV AEAD tests that inspect returned IV/ciphertext layout, SEC era matrix testing for pre-DKP versus DKP split-key behavior, and hardware QI tests that exercise non-contiguous scatterlists. Descriptor debug dumps can be compared against expected command lengths and key-inline decisions, but functional tag verification and IV/counter continuation tests are stronger end-to-end signals.
