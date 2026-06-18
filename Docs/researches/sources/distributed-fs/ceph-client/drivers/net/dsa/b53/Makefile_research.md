# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Makefile

Purpose: maps B53 Kconfig symbols to common, transport, and SerDes object files.

Important APIs/types/functions: `CONFIG_B53` builds `b53_common.o`; transport configs build `b53_spi.o`, `b53_mdio.o`, `b53_mmap.o`, `b53_srab.o`; `CONFIG_B53_SERDES` builds `b53_serdes.o`.

Control flow: Kbuild includes each object as built-in or module according to its tristate value. Transport modules call exported common symbols.

State and persistence behavior: Build artifacts only.

Dependencies and integration points: Depends on Kconfig constraints and symbol exports from common/SerDes source files.

Risks: module link failures if common exports or optional SerDes guards drift; new transport files require both Kconfig and Makefile updates.

Test signals: `make M=drivers/net/dsa/b53` across `y/m/n` combinations and SRAB with/without SerDes.
