# sources/distributed-fs/ceph-client/net/tipc/Kconfig

## Purpose
This Kconfig file exposes the Transparent Inter Process Communication protocol and optional TIPC media, crypto, and diagnostic features.

## Important APIs, Types, And Functions
Symbols are `TIPC`, `TIPC_MEDIA_IB`, `TIPC_MEDIA_UDP`, `TIPC_CRYPTO`, and `TIPC_DIAG`. `TIPC` is tristate and depends on `INET`; UDP media selects `NET_UDP_TUNNEL`; crypto selects `CRYPTO`, `CRYPTO_AES`, and `CRYPTO_GCM`; diagnostics are tristate and default to enabled when TIPC is enabled.

## Control Flow
There is no runtime control flow. Kconfig dependency and select logic determines which source objects and feature paths are compiled.

## State And Persistence
State is persisted in `.config`, controlling whether TIPC is built in, modular, or disabled, and whether optional media/encryption/diagnostic pieces are available.

## Dependencies And Integration Points
The options integrate TIPC with INET, IP-over-InfiniBand, UDP tunnel helpers, kernel crypto, and socket diagnostic tooling such as `ss`.

## Risks And Test Signals
Risks are missing optional dependencies and feature skew between enabled config and user-space `tipc` tooling. Test signals include allmodconfig builds, TIPC as built-in and module, UDP media default presence, crypto link tests, and `ss`/diagnostic netlink visibility.
