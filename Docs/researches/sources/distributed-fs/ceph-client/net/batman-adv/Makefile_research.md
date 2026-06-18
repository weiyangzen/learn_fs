# sources/distributed-fs/ceph-client/net/batman-adv/Makefile

## Purpose
The Makefile assembles the `batman-adv.o` composite object from mandatory routing/core objects and optional feature objects controlled by Kconfig.

## Important Build Rules
- `obj-$(CONFIG_BATMAN_ADV) += batman-adv.o` builds the module/built-in object.
- Mandatory objects include `bat_algo.o`, `bat_iv_ogm.o`, `bitarray.o`, fragmentation, gateway, hard-interface, hash, main, mesh-interface, netlink, originator, routing, send, tp_meter, translation-table, and tvlv.
- BATMAN V objects are conditional on `CONFIG_BATMAN_ADV_BATMAN_V`: `bat_v.o`, `bat_v_elp.o`, `bat_v_ogm.o`.
- Optional feature objects are gated for BLA, DAT, DEBUG, MCAST, and TRACING.
- `CFLAGS_trace.o := -I$(src)` ensures trace compilation can include local generated/source headers.

## Control Flow and Integration
The object list must match Kconfig and header stubs. For example, `bat_v.h` provides no-op helpers when BATMAN V objects are omitted, while BATMAN IV remains mandatory and registers the default routing algorithm.

## State and Persistence
No runtime state is stored here. Build composition determines which runtime algorithms, packet handlers, netlink/debug paths, and optimizations exist.

## Risks and Test Signals
Risks include missing objects for symbols referenced from always-built code, optional-object ordering issues, and feature symbols not matching Kconfig guards. Test signals include building with each optional feature toggled, `CONFIG_BATMAN_ADV_BATMAN_V=n`, tracing builds, and module link checks for unresolved symbols.
