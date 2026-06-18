# sources/distributed-fs/ceph-client/drivers/net/dsa/Makefile

Purpose: Kbuild mapping from DSA Kconfig symbols to top-level driver objects and vendor subdirectory traversal.

Important APIs/types/functions: `obj-$(CONFIG_...)` entries build objects such as `bcm-sf2.o`, `dsa_loop.o`, `mt7530*.o`, `lan9303*.o`, `vitesse-vsc73xx*.o`, and `yt921x.o`. `obj-y` descends into vendor directories including `b53/`.

Control flow: Kbuild appends each object when its config is `y` or `m`; subdirectories are visited unconditionally and gate their own objects internally.

State and persistence behavior: Build artifacts only; no runtime state.

Dependencies and integration points: Consumes top-level DSA Kconfig symbols and delegates B53 work to `drivers/net/dsa/b53/Makefile`.

Risks: Symbol/object name mismatches, stale compound object constituents, or ungated subdirectory objects can break builds.

Test signals: `make M=drivers/net/dsa`, allmodconfig/allnoconfig, and Kconfig-to-Makefile coverage checks.
