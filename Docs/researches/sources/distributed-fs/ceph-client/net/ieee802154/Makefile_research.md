## sources/distributed-fs/ceph-client/net/ieee802154/Makefile

Purpose: build recipe for the IEEE 802.15.4 networking subsystem and socket interface.

Important APIs/types/functions: `obj-$(CONFIG_IEEE802154) += ieee802154.o` builds the composite core. `obj-$(CONFIG_IEEE802154_SOCKET) += ieee802154_socket.o` builds socket support. `obj-y += 6lowpan/` always descends into the 6LoWPAN subdirectory, where its own Kconfig symbol selects objects. `ieee802154-y` includes `netlink.o`, `nl-mac.o`, `nl-phy.o`, `nl_policy.o`, `core.o`, `header_ops.o`, `sysfs.o`, `nl802154.o`, `trace.o`, and `pan.o`; `ieee802154_socket-y := socket.o`. `CFLAGS_trace.o := -I$(src)` supports trace header include generation.

Control flow and state: no runtime flow, but object composition defines module init coverage. `core.o` calls both legacy `ieee802154_nl_init()` and modern `nl802154_init()`, so corresponding objects must be linked.

Dependencies and integration points: driven by Kconfig symbols and kernel kbuild. Exposes trace support and subdirectory recursion to 6LoWPAN.

Risks: removing an object can create unresolved symbols or silently drop netlink/sysfs/PAN functionality. The unconditional subdirectory recursion is safe because child Makefile selection is symbol-gated.

Test signals: all relevant config builds, especially experimental nl802154, socket, and 6LoWPAN combinations; modpost and link checks.
