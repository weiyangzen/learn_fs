## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Kconfig

Purpose: Kconfig entry for IPv6 compression over IEEE 802.15.4. It defines `IEEE802154_6LOWPAN` as the configuration switch for building the 802.15.4-specific 6LoWPAN module.

Important APIs/types/functions: the `config IEEE802154_6LOWPAN` symbol is `tristate`, has prompt `6lowpan support over IEEE 802.15.4`, and depends on the generic `6LOWPAN` subsystem. Its help text states that it provides IPv6 compression over IEEE 802.15.4.

Control flow and state: no runtime state. Build selection controls whether `core.o`, `rx.o`, `reassembly.o`, and `tx.o` are linked into `ieee802154_6lowpan.o`.

Dependencies and integration points: sourced by `net/ieee802154/Kconfig` inside the parent `IEEE802154` menu. Requires generic 6LoWPAN support so compression/decompression helpers and lowpan netdevice support are available.

Risks: a missing `6LOWPAN` dependency would cause unresolved symbols; the current dependency prevents that. Because this is a tristate, module/built-in combinations with parent IEEE802154 and generic 6LOWPAN must remain compatible.

Test signals: Kconfig build matrix for disabled, module, and built-in combinations; `make oldconfig` visibility under `IEEE802154`; symbol-driven inclusion of `ieee802154_6lowpan.o`.
