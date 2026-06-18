# sources/distributed-fs/ceph-client/drivers/net/ppp/Makefile

Purpose: Maps PPP Kconfig symbols to the object files built under `drivers/net/ppp`.

Important mappings: `CONFIG_PPP` builds `ppp_generic.o`; async/sync tty support builds `ppp_async.o` and `ppp_synctty.o`; compressor options build `bsd_comp.o`, `ppp_deflate.o`, and `ppp_mppe.o`; PPPoE builds `pppox.o pppoe.o`; PPPoL2TP builds `pppox.o`; PPTP builds `pppox.o pptp.o`.

Control flow and state: Kbuild expands each `obj-$(CONFIG_...)` entry as built-in, module, or omitted according to the tristate. `pppox.o` is intentionally shared by multiple PPP-over-X transports. There is no runtime state; the file only controls generated objects/modules.

Dependencies and integration points: Depends on Kconfig to enforce prerequisites and on `ppp_generic.o` exporting channel/compressor symbols consumed by tty/channel and compression modules. Module autoload aliases are declared in the C files, not here.

Risks and test signals: Mismatches between this list and Kconfig can create missing modules or unresolved symbols. Multi-transport PPPoX configs must produce one usable common `pppox` provider. Test minimal PPP, async/sync tty, each compressor, PPPoE-only, PPPoL2TP-only, PPTP-only, and combined PPPoX transport builds.
