# sources/distributed-fs/ceph-client/include/soc/fsl/caam-blob.h

Purpose: declares CAAM hardware blob encapsulation/decapsulation support and protected-key metadata.

Important APIs and types: constants define key modifier size, blob overhead, maximum blob length, CCM/ECB protected-key algorithms, nonce/ICV sizes, and CCM overhead. `struct caam_pkey_info` is a packed protected-key header with protected flag, encryption algorithm, plain key size, and flexible key buffer. `struct caam_blob_info` describes input/output DMAable buffers, lengths, key modifier, and embedded protected-key info. APIs include `caam_blob_gen_init()`, `caam_blob_gen_exit()`, `caam_process_blob()`, and inline `caam_encap_blob()`/`caam_decap_blob()` length validators.

Control flow: clients initialize a CAAM blob context, prepare DMAable input/output/key-modifier buffers, call encapsulation or decapsulation, and release the context. The inline wrappers reject impossible output/input sizes before submitting hardware work.

State and persistence: blob context and job-ring resources are runtime state. Produced blobs are persistent encrypted material outside this header; key security depends on CAAM hardware and key modifiers.

Dependencies and integration points: depends on types/errno and integrates trusted key, crypto, NVMEM, or storage users needing CAAM-sealed secrets.

Risks and test signals: risks include non-DMAable buffers, output length underestimation, key modifier length overrun, algorithm/header mismatch, and leaking protected key material. Test init failure without hardware, encap/decap round trips, boundary lengths, invalid key modifiers, DMA mapping errors, and both CCM/ECB protected-key forms.
