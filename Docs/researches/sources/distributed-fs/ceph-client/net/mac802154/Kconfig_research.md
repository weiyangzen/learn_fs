# sources/distributed-fs/ceph-client/net/mac802154/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_MAC802154`, the generic IEEE 802.15.4 SoftMAC networking stack for devices that implement only PHY-level behavior.

## Important APIs, Types, And Functions
The symbol is `MAC802154`, a tristate option named "Generic IEEE 802.15.4 Soft Networking Stack (mac802154)". It depends on `IEEE802154` and selects `CRC_CCITT`, `CRYPTO`, `CRYPTO_AUTHENC`, `CRYPTO_CCM`, `CRYPTO_CTR`, and `CRYPTO_AES`.

## Control Flow
Kconfig controls whether the mac802154 object set is built in, built as a module, or omitted. There is no runtime control flow in this file.

## State And Persistence
The selected config persists in the kernel build configuration. Runtime state is created by the compiled mac802154 module/files.

## Dependencies And Integration Points
The selected crypto dependencies support link-layer security implementation in `llsec.c` and related cfg/iface hooks. The `IEEE802154` dependency ensures the common WPAN/cfg802154 infrastructure exists.

## Risks And Edge Cases
The help text explicitly warns that the implementation is not certified or feature complete. Disabling required crypto selects would break LLSEC build/runtime behavior, so dependency changes require full build coverage.

## Test Signals
Build matrix coverage should include `MAC802154=y`, `MAC802154=m`, and disabled, with IEEE802154 enabled. Module load/unload and LLSEC crypto availability are useful integration signals.
