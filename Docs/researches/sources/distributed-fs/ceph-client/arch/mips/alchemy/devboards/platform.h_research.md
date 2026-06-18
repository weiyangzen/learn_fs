## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.h

Purpose: declares shared helper functions used by the Alchemy devboard source files. It keeps PCMCIA and NOR flash registration prototypes in one local header.

Important APIs and types: `db1x_register_pcmcia_socket()` takes attribute, memory, and I/O physical ranges plus card-detect/card/status/eject IRQs and a socket ID. `db1x_register_norflash()` takes total flash size, bus width, and swapboot state. Both are marked `__init`, matching their implementation and call sites.

Control flow: none in the header. It enables per-board setup files to call helpers implemented in `platform.c`.

State and persistence: none directly. The declared helpers create platform devices and MTD partition descriptors at runtime.

Dependencies and integration: includes `linux/init.h` for `__init` and relies on `phys_addr_t` being available through included kernel headers at call sites. It is included by DB1000/1200/1300/1550 platform setup code.

Risks: the prototype parameter name for `pcmcia_attr_end` is written as `pcmcia_attr_len`, while the implementation treats it as an end address. This is naming-only but can mislead future callers. Any signature drift from `platform.c` would break all board files at compile time.

Test signals: compile coverage is the primary signal. Runtime validation comes indirectly from PCMCIA and NOR flash platform devices registered by board files.
