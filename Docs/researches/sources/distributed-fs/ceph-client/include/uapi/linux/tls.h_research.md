# sources/distributed-fs/ceph-client/include/uapi/linux/tls.h

Purpose: Defines the Linux kernel TLS UAPI for socket options, protocol versions, supported ciphers, crypto parameter structures, and TLS netlink/info attributes.

Important APIs/types/functions: Socket options include `TLS_TX`, `TLS_RX`, TX zerocopy read-only, opportunistic RX no-padding, and max TX payload length. Version helpers encode/decode TLS 1.2 and 1.3. Cipher constants cover AES-GCM-128/256, AES-CCM-128, ChaCha20-Poly1305, SM4-GCM/CCM, and ARIA-GCM-128/256 with per-cipher IV, key, salt, tag, and record-sequence sizes. `struct tls_crypto_info` is the common version/cipher prefix; cipher-specific `tls12_crypto_info_*` structs append keying material. TLS info enum exposes version, cipher, TX/RX config, zerocopy, no-pad, and payload length. Config states include base, software, hardware, and hardware-record modes.

Control flow: Userspace configures a TCP socket with `setsockopt(SOL_TLS, TLS_TX/TLS_RX, struct tls*_crypto_info_*)`; the kernel validates version/cipher and key lengths, then performs software or device-offloaded record processing. Info attributes are used for querying negotiated kernel TLS state.

State and persistence behavior: TLS crypto state lives in the socket and lasts until socket close or reconfiguration permitted by the kernel. Record sequence arrays are caller-provided starting state, so reuse or incorrect endianness can compromise security.

Dependencies and integration points: Includes `linux/types.h`; integrates with kTLS, TCP sockets, crypto API, NIC TLS offload, sendfile zerocopy, and netlink/diagnostic reporting.

Risks: ABI structs carry raw keying material and must be exact size. Ciphers differ in salt/IV layout, notably ChaCha20-Poly1305 salt size zero and 12-byte IV. Record sequence handling, version/cipher mismatches, and hardware-offload fallback are security-sensitive.

Test signals: Compile userspace against all structs, configure TX/RX for each supported cipher, test TLS 1.2/1.3 version rejection paths, verify record sequence progression, query `TLS_INFO_*`, and run kTLS selftests with software and offload paths.
