# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_crypto.h

Purpose: defines the virtio crypto accelerator ABI for session creation/destruction and data requests across cipher, hash, MAC, AEAD, and asymmetric cipher services.

Important APIs/types/functions: service IDs and `VIRTIO_CRYPTO_OPCODE()` compose control/data opcodes. Control structs include `virtio_crypto_ctrl_header`, service-specific session parameter structs, `virtio_crypto_sym_create_session_req`, `virtio_crypto_destroy_session_req`, and `virtio_crypto_op_ctrl_req`. Data structs include `virtio_crypto_op_header`, cipher/hash/MAC/AEAD/algorithm-chain/akcipher parameter structs, and `virtio_crypto_op_data_req`. Config and response structs include `virtio_crypto_config`, `virtio_crypto_session_input`, `virtio_crypto_inhdr`, status codes (`OK`, `ERR`, `BADMSG`, `NOTSUPP`, `INVSESS`, `NOSPC`, `KEY_REJECTED`), and hardware-ready status `VIRTIO_CRYPTO_S_HW_READY`.

Control flow: the driver reads `virtio_crypto_config` to learn service/algorithm masks, queue counts, key limits, and max request size. It creates sessions on the control virtqueue by sending a header plus service-specific parameters and key material in the descriptor chain, receives a session ID/status, then submits data requests on data virtqueues with opcode, algorithm, session ID, operation flags, lengths, IV/AAD/source/destination buffers, and receives a status in `virtio_crypto_inhdr`. Sessions are explicitly destroyed on the control queue.

State and persistence: device state includes supported algorithm masks, session table entries keyed by 64-bit session ID, per-queue data processing, and possibly accelerator hardware readiness. Session state persists until destroy or reset. Request buffers and IV/counter updates are per-operation/transient.

Dependencies and integration: includes Linux and virtio type/id/config headers. It integrates with guest crypto APIs, VMM or hardware crypto backends, virtqueues, and algorithm-specific standards for AES, DES/3DES, KASUMI, SNOW3G, ZUC, SHA/SHA3, HMAC/CMAC/GMAC, AEAD GCM/CCM/ChaCha20-Poly1305, RSA, DSA, and ECDSA.

Risks: all request lengths drive descriptor parsing and must match buffer chains. Unsupported or deprecated algorithms/opcodes need clear `NOTSUPP`/error behavior. Session IDs are device-generated and invalid after destroy/reset. AEAD and algorithm-chain offsets/AAD/hash lengths are easy to miscompute. Cryptographic key material crosses the virtqueue boundary, so zeroization and isolation are important in implementations.

Test signals: algorithm negotiation tests, session create/destroy lifecycle tests, known-answer tests for each supported algorithm/mode, invalid session/status tests, max request/key length tests, multi-queue concurrency tests, AEAD authentication failure tests, and ABI layout checks.
