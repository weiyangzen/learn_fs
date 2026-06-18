# sources/distributed-fs/ceph-client/drivers/pcmcia/cs_internal.h

Purpose: Defines private contracts shared inside the PCMCIA core modules. It separates internal state flags, resource operation hooks, callback types, and cross-module prototypes from public PCMCIA driver headers.

Important APIs and types: Defines `config_t`, `struct cis_cache_entry`, `struct pccard_resource_ops`, `struct pcmcia_callback`, `BIND_FN_ALL`, client/window/socket state flags, sysfs event masks, and prototypes for socket sysfs, CardBus, resource, CIS, and bus-core functions.

Control flow: No direct execution. The function pointer types determine how resource managers, socket core, and bus services call each other.

State and persistence: `config_t` and `cis_cache_entry` describe runtime state embedded or referenced from `struct pcmcia_device` and `struct pcmcia_socket`. State flags such as `CONFIG_LOCKED`, `CONFIG_IO_REQ`, `SOCKET_PRESENT`, `SOCKET_CARDBUS`, and `SOCKET_WIN_REQ()` gate lifecycle transitions.

Dependencies and integration points: Included by `cs.c`, `ds.c`, `cistpl.c`, `pcmcia_cis.c`, `pcmcia_resource.c`, and `cardbus.c`, but explicitly not by socket or device drivers. It binds module layering between `pcmcia_core`, `pcmcia`, and `pcmcia_rsrc`.

Risks: Because this header is a private ABI between separately linked PCMCIA modules, signature or flag changes can create subtle cross-module breakage. Public driver behavior can still be affected indirectly by these private state definitions.

Test signals: Full PCMCIA modular build, symbol resolution between `pcmcia_core` and `pcmcia`, and lifecycle tests that exercise every callback in `struct pcmcia_callback`.
