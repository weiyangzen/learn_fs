# sources/distributed-fs/ceph-client/include/net/ife.h

Purpose: declares Intermediate Functional Block Encapsulation metadata helpers used by tc actions to attach or remove metadata TLVs around Ethernet frames.

Important APIs: when `CONFIG_NET_IFE` is enabled, `ife_encode()` and `ife_decode()` add/remove IFE encapsulation and return data pointers/metadata length. TLV helpers decode, encode, and advance metadata entries: `ife_tlv_meta_decode()`, `ife_tlv_meta_encode()`, and `ife_tlv_meta_next()`. When disabled, inline stubs return `NULL` or zero.

Control flow and state: encode/decode operates directly on skb data, while TLV helpers walk variable-length metadata. No persistent state is declared in this header.

Dependencies and integration: depends on Ethernet device helpers, rtnetlink, and UAPI IFE definitions. It integrates with tc IFE actions and metadata classifiers/actions.

Risks: disabled stubs can make callers silently skip behavior. TLV parsing must validate lengths and end pointers to avoid overreads. Tests should cover encode/decode round trips, multiple TLVs, malformed TLV lengths, metadata length accounting, config-disabled stubs, and tc action integration.
