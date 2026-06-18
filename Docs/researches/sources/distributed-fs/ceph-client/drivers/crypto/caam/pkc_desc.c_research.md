<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c

Purpose: builds CAAM job descriptors for RSA public and private-key operations. Public key cryptography uses job descriptors directly because there is no shared descriptor for these operations.

Important APIs and control flow: `init_rsa_pub_desc()` initializes a job descriptor with RSA public PDB size, appends SG flags, input/output/modulus/exponent DMA pointers, input length, and `OP_PCLID_RSAENC_PUBKEY`. `init_rsa_priv_f1_desc()` appends encrypted input, output, modulus, private exponent, and private key form 1 operation. `init_rsa_priv_f2_desc()` appends private form 2 parameters including p/q and temporary buffers. `init_rsa_priv_f3_desc()` appends CRT coefficient, p/q, dp/dq, temporaries, length, and form 3 operation.

State and persistence behavior: no persistent state. The caller owns PDB contents, DMA mappings, temporary buffers, and descriptor memory; these helpers only append words to the descriptor.

Dependencies and integration points: depends on RSA PDB structs and size macros from CAAM PKC headers/PDB definitions and descriptor construction helpers. Called by CAAM akcipher/RSA implementation.

Risks and test signals: risks include no validation of key/input lengths, pointer DMA mapping, temporary buffer sizes, or descriptor capacity; wrong key form selection silently produces hardware errors. Test signals include RSA encrypt/decrypt/sign/verify known-answer tests for public, raw private, and CRT forms; descriptor dumps matching expected PDB order; and hardware error indexes pointing to intended fields on malformed keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c -->
