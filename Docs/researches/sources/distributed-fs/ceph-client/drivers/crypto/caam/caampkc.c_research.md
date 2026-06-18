# sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.c

## Purpose
`caampkc.c` implements CAAM public-key cryptography support for RSA through the kernel akcipher API. It registers an async `rsa-caam` implementation when PKHA hardware is available, parses public/private keys, supports CAAM RSA private key forms 1/2/3, builds per-request job descriptors containing PDBs and SG pointers, submits jobs to CAAM job rings, and handles completion/unmapping.

## Important APIs, Types, And Functions
Request cleanup is split across `rsa_io_unmap()`, `rsa_pub_unmap()`, and `rsa_priv_f{1,2,3}_unmap()`. Completion callbacks are `rsa_pub_done()` and `rsa_priv_f_done()`. `rsa_edesc_alloc()` normalizes input length by stripping leading zeros or adding zero padding, maps source/destination SGs, builds optional SEC4 SG tables, and stores the edesc in request context. PDB setup functions are `set_rsa_pub_pdb()`, `set_rsa_priv_f1_pdb()`, `set_rsa_priv_f2_pdb()`, and `set_rsa_priv_f3_pdb()`.

Crypto API operations are `caam_rsa_enc()`, `caam_rsa_dec()`, and private-form dispatch helpers. Key handling uses `caam_rsa_set_pub_key()`, `caam_rsa_set_priv_key()`, `caam_rsa_set_priv_key_form()`, `caam_read_raw_data()`, `caam_read_rsa_crt()`, and `caam_rsa_free_key()`. Transform lifetime is managed by `caam_rsa_init_tfm()` and `caam_rsa_exit_tfm()`. Module hooks are `caam_pkc_init()` and `caam_pkc_exit()`.

## Control Flow
Initialization checks PKHA availability from perfmon or version registers and skips registration if encryption/decryption is unavailable. It allocates a zero buffer used for left-padding short RSA inputs, then registers the akcipher engine algorithm. Transform init allocates a job ring and maps the zero padding buffer. Key set parses ASN.1 RSA keys into raw fields, strips leading zeros from positive integers, validates modulus length up to 4096 bits, allocates key buffers, and chooses the best private form available.

Encrypt/decrypt validate key presence and destination length, allocate an edesc, map key fields into the selected PDB, initialize a CAAM RSA descriptor, and submit directly to the job ring or through crypto-engine when backlog is requested. Completion decodes CAAM errors, unmaps key/PDB/source/destination/SG DMA, frees the edesc, and completes the akcipher request directly or through `crypto_finalize_akcipher_request()`.

## State And Persistence Behavior
Global state consists of `zero_buffer` and `init_done`. Per-transform state in `caam_rsa_ctx` holds parsed key buffers, job-ring device, and mapped padding DMA. Per-request state in `caam_rsa_req_ctx` stores stripped/padded source SG information, edesc pointer, and completion callback. Key buffers are freed with `kfree_sensitive()` where private material is involved; public `e`/`n` use regular `kfree()`.

## Dependencies And Integration Points
The file depends on CAAM job-ring APIs, crypto-engine akcipher support, RSA parser helpers, CAAM PDB definitions and descriptor constructors from `caampkc.h`, SEC4 SG helpers, DMA mapping, scatterwalk helpers, and CAAM error decoding. It registers a single akcipher algorithm named `rsa` with driver name `rsa-caam`.

## Risks
RSA input normalization is subtle: oversized inputs strip leading zeros; shorter inputs use DMA-mapped zero padding in the SG table. Bugs can alter numeric values or PDB lengths. PDB setup maps many key buffers with multi-label unwind paths, making unmap symmetry critical. `akcipher_do_one_req()` always calls `rsa_pub_unmap()` on enqueue failure even though backlog requests may be private operations, which is a code path worth reviewing carefully against engine usage. CRT handling must zero-pad dP/dQ/qInv to factor lengths and avoid accepting zero-only fields. Hardware capability checks differ before and after era 10.

## Test Signals
Signals include `caam pkc algorithms registered in /proc/crypto` and an `rsa-caam` entry. Tests should cover public encrypt/private decrypt with form1, form2, and form3 keys; leading-zero modulus/key fields; leading-zero ciphertext/plaintext inputs; short input padding; fragmented source/destination SGs; too-small destination buffers; invalid key lengths over 4096 bits; missing PKHA hardware; backlog and direct completion paths; and removal after failed registration.
