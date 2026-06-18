# sources/distributed-fs/ceph-client/drivers/pcmcia/yenta_socket.c

Purpose: Implements the generic Yenta-compatible PCI CardBus bridge driver. It supports CardBus and 16-bit PC Card sockets, resource-window allocation, socket power/status/map operations, interrupt/polling event delivery, chipset-specific overrides, sysfs register dumps, and suspend/resume.

Important APIs and functions: The module registers `yenta_cardbus_driver`. Core PCMCIA ops are `yenta_sock_init()`, `yenta_sock_suspend()`, `yenta_get_status()`, `yenta_set_socket()`, `yenta_set_io_map()`, and `yenta_set_mem_map()`. Probe/remove are `yenta_probe()` and `yenta_close()`. Resource helpers include `yenta_allocate_resources()`, `yenta_allocate_res()`, and `yenta_search_res()`. IRQ helpers include `yenta_interrupt()`, polling wrapper, ISA/PCI probe helpers, and capability discovery.

Control flow: Probe validates a subordinate bus, allocates a `yenta_socket`, enables and requests PCI resources, maps the CardBus register BAR, initializes bridge config, disables events, allocates bridge I/O/memory windows, applies vendor override callbacks selected by PCI IDs, requests a PCI IRQ or starts polling, interrogates voltage/card type, probes ISA IRQ mask, fixes parent bridge bus numbers, registers the PCMCIA socket, and creates `yenta_registers`. Runtime interrupts clear CardBus event and ExCA CSC status, translate events, and call `pcmcia_parse_events()`.

State and persistence: `struct yenta_socket` stores PCI device, IRQ routing, mapped register base, timer, embedded socket, vendor type, flags, probe status, private vendor data, and saved PCI state. Hardware state persists in CardBus memory-mapped registers, ExCA registers, and PCI bridge config/resource windows.

Dependencies and integration points: Depends on PCI, PCMCIA socket services, `pccard_nonstatic_ops`, `i82365.h`, and optional TI/Ricoh/Toshiba/O2 headers. It integrates CardBus subordinate PCI buses with PCMCIA card services.

Risks: This driver programs power and resource windows directly and supports many legacy bridge quirks. Polling mode disables CardBus support when no PCI IRQ is available. Resource allocation may continue with missing windows. Power-on can trigger interrupt storms on some TI chips, mitigated by vendor hooks. Parent bridge bus-number fixups touch PCI topology.

Test signals: Probe on generic and vendor-specific CardBus bridges, CardBus and 16-bit card insertion/removal, PCI IRQ and polling modes, bridge resource assignment, I/O and memory map programming, socket power/reset/Vpp transitions, sysfs register dump, suspend/resume, and vendor override logs.
