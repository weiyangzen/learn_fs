<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h

Purpose: this header defines the Linux kernel TLS socket option ABI for configuring TLS offload/ktls crypto parameters.

Important APIs/types: `TLS_TX` and `TLS_RX` select transmit/receive parameters. Version helpers compose and split TLS version numbers; this header defines TLS 1.2. AES-GCM-128 constants define cipher ID and IV/key/salt/record-sequence sizes. `struct tls_crypto_info` carries version and cipher type; `struct tls12_crypto_info_aes_gcm_128` appends the cipher material. `TLS_SET_RECORD_TYPE` and `TLS_GET_RECORD_TYPE` are control options.

Control flow: userspace performs the handshake itself, then calls `setsockopt` with TLS_TX/TLS_RX and a cipher-specific crypto-info struct to hand record encryption/decryption to the kernel.

State and persistence: configured crypto state persists on the socket. Record sequence values and keys are sensitive and must match userspace TLS state exactly.

Dependencies/integration: depends on `linux/types.h`; integrated by OpenSSL/ktls users, NIC offload paths, and TCP ULP (`TCP_ULP`) setup.

Risks and test signals: risks include key material exposure, struct-size/cipher mismatch, unsupported TLS versions/ciphers, record sequence errors, and option ordering. Test successful ktls send/receive, fallback on unsupported kernels, and record type get/set where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/tls.h -->
