# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.h

### Purpose
`otx_cptvf_algs.h` defines CPT crypto operation opcodes, cipher/MAC identifiers, control words, transform contexts, request contexts, and algorithm registration APIs for the OcteonTX VF crypto layer.

### Important APIs, Types, And Functions
Important enums define request types, major opcodes, AE/SE request classification, cipher types, MAC types, and AES key length encodings. Key structures and unions are `union otx_cpt_encr_ctrl`, `struct otx_cpt_enc_context`, `union otx_cpt_fchmac_ctx`, `struct otx_cpt_fc_ctx`, `struct otx_cpt_enc_ctx`, `struct otx_cpt_des3_ctx`, `union otx_cpt_offset_ctrl_word`, `struct otx_cpt_req_ctx`, `struct otx_cpt_sdesc`, and `struct otx_cpt_aead_ctx`. It declares `otx_cpt_crypto_init()` and `otx_cpt_crypto_exit()`.

### Control Flow, State, And Persistence
The structures are embedded in crypto transform and request contexts. Per-transform state holds keys, key types, hash algorithms, HMAC pads, and AEAD configuration. Per-request state combines a CPT request manager object, an offset control word, and flexicrypto context sent to hardware as gather-list inputs.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on crypto hash APIs, shared CPT type enums, and request-manager definitions. Risks include endian-sensitive control-word bitfields, max key size layout for combined auth/encryption keys, XTS second key offset assumptions, and mismatches between algorithm code and microcode opcode expectations. Test signals include compile coverage on endian variants, algorithm request context sizing, AES key length mapping, authenc key parsing, GCM salt/IV layout, and hardware command dumps.
