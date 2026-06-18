## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Makefile

Purpose: build recipe for the IEEE 802.15.4 6LoWPAN implementation.

Important APIs/types/functions: `obj-$(CONFIG_IEEE802154_6LOWPAN) += ieee802154_6lowpan.o` selects the composite object. `ieee802154_6lowpan-y := core.o rx.o reassembly.o tx.o` declares the constituent source files.

Control flow and state: no runtime behavior. The object composition maps directly to module responsibilities: netdevice/rtnl integration in `core.o`, packet receive in `rx.o`, inet-frag reassembly in `reassembly.o`, and transmit compression/fragmentation in `tx.o`.

Dependencies and integration points: controlled by the Kconfig symbol from `Kconfig` and included through the parent IEEE 802.15.4 Makefile's `obj-y += 6lowpan/` recursion.

Risks: omissions here silently remove functionality at link time. All four objects are required because `core.c` references RX and frag init/exit, netdev ops reference TX/header functions, and RX references reassembly.

Test signals: build with `CONFIG_IEEE802154_6LOWPAN=m/y`; modpost symbol resolution; module load proving `module_init()` and `module_exit()` are included.
