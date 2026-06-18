# sources/distributed-fs/ceph-client/net/tls/Kconfig

## Purpose
Defines kernel configuration switches for kTLS core support, hardware offload, and legacy TCP stack bypass offload.

## Important Options
`CONFIG_TLS` is a tristate depending on `INET` and selecting crypto, AES, GCM, and `NET_SOCK_MSG`; it enables in-kernel symmetric TLS record handling. `CONFIG_TLS_DEVICE` is a bool depending on TLS and selecting decrypted-skb, xmit-validation, and RX queue mapping support for NIC TLS offload. `CONFIG_TLS_TOE` is a bool for legacy TCP offload engine semantics incompatible with normal Linux networking stack behavior.

## Control Flow And State
Kconfig has no runtime state, but it controls which objects and inline stubs are built. `TLS_DEVICE` gates `tls_device.c` and `tls_device_fallback.c`, plus real functions in `tls.h` instead of `-EOPNOTSUPP` stubs. `TLS_TOE` gates `tls_toe.o`.

## Dependencies And Integration Points
The selections ensure crypto AEAD primitives and socket-message infrastructure are present for software kTLS. Device offload selections enable decrypted skb tagging, xmit validation hooks, and socket RX queue mapping needed by NIC offload drivers.

## Risks And Test Signals
Risks include unexpected feature availability when TLS is modular, missing selected dependencies for device offload, and enabling TOE semantics in environments expecting normal TCP stack behavior. Test signals include allmodconfig/allyesconfig builds, TLS without device offload builds using `tls.h` stubs, and runtime kTLS setsockopt tests under software and hardware-offload configurations.
