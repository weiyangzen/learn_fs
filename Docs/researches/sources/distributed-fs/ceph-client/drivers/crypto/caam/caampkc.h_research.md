# sources/distributed-fs/ceph-client/drivers/crypto/caam/caampkc.h

## Purpose
`caampkc.h` defines the RSA public-key crypto data structures and descriptor constructor declarations used by the CAAM PKC implementation. It documents the CAAM-supported RSA private key representations and the per-transform/per-request/per-edesc state layouts.

## Important APIs, Types, And Functions
`enum caam_priv_key_form` enumerates `FORM1` `(n,d)`, `FORM2` `(p,q,d)`, and `FORM3` `(p,q,dP,dQ,qInv)`. `struct caam_rsa_key` stores raw key component buffers, temporary buffers for CAAM private operations, component sizes, and selected private form. `struct caam_rsa_ctx` stores the key, job-ring device, and DMA address of the shared zero-padding buffer. `struct caam_rsa_req_ctx` stores source fixup SG state, edesc pointer, and the selected completion callback. `struct rsa_edesc` stores SG counts, mapped counts, SEC4 SG metadata, backlog flag, one RSA PDB union, and trailing hardware descriptor words.

The declared descriptor constructors are `init_rsa_pub_desc()`, `init_rsa_priv_f1_desc()`, `init_rsa_priv_f2_desc()`, and `init_rsa_priv_f3_desc()`.

## Control Flow
The header has no runtime control flow, but its form enum drives `caam_rsa_dec()` dispatch and completion unmapping. The PDB union layout lets each operation allocate one edesc and then initialize the matching descriptor form in `caampkc.c`.

## State And Persistence Behavior
The structures describe volatile kernel memory. `caam_rsa_key` persists for a crypto transform until a new key is installed or the transform exits. `caam_rsa_req_ctx` and `rsa_edesc` persist only for one in-flight akcipher request. DMA addresses in PDBs and SG tables are valid only while mapped.

## Dependencies And Integration Points
The header includes CAAM compatibility and PDB definitions. It is consumed by `caampkc.c` and by RSA descriptor construction code that supplies the declared `init_rsa_*_desc()` functions. It integrates CAAM PDB formats with Linux akcipher request state.

## Risks
The documentation has a duplicated `@dp` tag where one entry refers to `dq`, so readers must rely on field names. Layout changes to `rsa_edesc` can break allocation math in `rsa_edesc_alloc()`, which places `sec4_sg` after `hw_desc`. Private key buffers require sensitive free handling in implementation. The form enum must stay aligned with PDB setup and unmap dispatch.

## Test Signals
Compile coverage verifies structure and constructor users. Runtime coverage comes from RSA selftests across all private key forms, SG fragmentation, padding, and cleanup paths. Memory sanitizers or DMA debug are useful for catching PDB/SG layout or unmap mistakes tied to these definitions.
