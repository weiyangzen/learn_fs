# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption.go

Purpose: Implements Linux encrypted overlay data-plane support using IPsec/XFRM transport mode plus firewall rules that force VXLAN traffic for secure VNIs through encryption.

Important APIs and types: constants define XFRM mark and ESP packet expansion. `key`, `spi`, `encrNode`, and `encrMap` model encryption keys and per-peer SAs. `setupEncryption` programs reverse SAs for all keys and bidirectional SA/SP for the primary key. `removeEncryption` reference-counts peers and removes SAs/SPs. `programMangle`, `programInput`, and `programOverlayEncryptionFirewall` manage iptables/nftables firewall enforcement. `programSA`, `programSP`, `saExists`, `spExists`, `buildSPI`, and `buildAeadAlgo` manipulate XFRM state/policies. `setKeys`, `updateKeys`, `updateNodeKey`, `maxMTU`, and `clearEncryptionStates` manage key lifecycle and cleanup.

Control flow: encryption setup requires keys and uses `encrMu`; primary key is index 0. Key rotation can add a key, promote primary, and prune old keys while updating per-node XFRM objects in an order intended to maintain connectivity. Firewall programming uses nftables when enabled, otherwise iptables mangle/filter rules. Failure to determine transport table fails closed for encrypted setup.

State and persistence: no datastore. Kernel XFRM state/policies and iptables/nftables rules are persistent kernel side effects until cleanup. In-memory `secMap` tracks peer counts and SPI lists; `keys` holds active key material.

Dependencies and integration points: used by overlay peer add/delete and network subnet initialization. Depends on netlink XFRM, overlayutils VXLAN port, iptables, nftables, discovery encryption notifications, and driver bind/advertise addresses.

Risks: high side-effect surface with partial failure logging. `programSP` assumes forward/reverse SA pointers are non-nil for primary operations. Key strings reveal a short key prefix in debug output. Correctness depends on lock hierarchy and on matching advertise/bind address families. Packet MTU calculation must match ESP overhead.

Test signals: `encryption_test.go` verifies SPI compatibility with legacy hashing for IPv4/IPv6 forms; there are no full XFRM programming integration tests here.
