# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.c

### Purpose
`otx_cptvf_algs.c` registers and implements the Linux crypto API algorithms backed by OcteonTX CPT VFs. It formats skcipher and AEAD requests into CPT flexicrypto/HMAC command inputs, manages key material and HMAC pads, dispatches requests to an SE VF, and handles async callbacks.

### Important APIs, Types, And Functions
Public APIs are `otx_cpt_crypto_init()` and `otx_cpt_crypto_exit()`. Key internals include device tables `se_devices` and `ae_devices`, `get_se_device()`, callbacks `otx_cpt_skcipher_callback()` and `otx_cpt_aead_callback()`, skcipher formatting (`create_ctx_hdr()`, `create_input_list()`, `create_output_list()`, `cpt_enc_dec()`), key setters for AES/DES3/XTS, AEAD init/exit/authsize/setkey helpers, HMAC pad setup (`aead_hmac_init()`), AEAD list builders, null-cipher HMAC verification, and registration arrays `otx_cpt_skciphers` and `otx_cpt_aeads`.

### Control Flow, State, And Persistence
VF probe calls `otx_cpt_crypto_init()` after PF group binding; SE VFs are added to a sorted table, and algorithms register only after the expected number of devices is present. Each crypto request clears request context, builds control words, FC/HMAC context, input and output buffer pointer arrays, assigns callback and metadata, selects an SE device, and calls `otx_cpt_do_request()`. Completion callbacks clean DMA/request buffers and complete the original crypto async request; skcipher callbacks also copy back CBC IV state. Key setup persists cipher keys, auth keys, derived HMAC ipad/opad hash states, AES key type, auth size, and truncation flags in transform context. `crypto_exit` removes the VF from the device table and unregisters algorithms only when the last SE device disappears and algorithms are not in use.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Linux skcipher/AEAD/authenc APIs, shash providers, scatterwalk, request-manager DMA cleanup, VF device registration, module refs, and crypto algorithm refcounts. Risks include scatterlist virtual-address assumptions via `sg_virt()`, request-size and SG-count limits, IV copyback for in-place CBC decrypt, null-cipher HMAC manual verification, truncated HMAC status handling, algorithm registration lifetime with multiple VFs, and refusing skcipher registration under `CONFIG_DM_CRYPT`. Test signals include AES CBC/ECB/XTS, 3DES CBC/ECB, authenc HMAC-SHA CBC-AES, null-cipher HMAC, RFC4106 GCM, truncated auth sizes, in-place and out-of-place SGs, request size > 65535, VF hot-unplug while algorithms are referenced, and crypto manager async tests.
