# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.c

Purpose: Acorn expansion-card bus implementation. It probes podule slots, reads card IDs/chunk directories, provides card resources, dispatches expansion-card interrupts, exposes sysfs/proc data, and implements ecard driver binding.

Important APIs/types/functions: public APIs include `ecard_readchunk()`, `ecard_request_resources()`, `ecard_release_resources()`, `ecard_setirq()`, `ecardm_iomap()`, `ecard_register_driver()`, `ecard_remove_driver()`, and `ecard_bus_type`. Core internals include `ecard_task()`, `ecard_readbytes()`, `ecard_probe()`, `ecard_irq_handler()`, `__ecard_address()`, and ecard bus probe/remove/shutdown methods.

Control flow: `postcore_initcall` registers the bus; `subsys_initcall` allocates IRQ descriptors, starts `kecardd`, probes slots 0-7 as EASI then IOC, probes network slot 8, installs a chained IRQ handler, and creates `/proc/bus/ecard/devices`. Loader-dependent reads are marshalled to `kecardd`, whose custom mm maps legacy I/O windows. Drivers match by manufacturer/product or simple ID, claim the card, request resources, and install IRQ ops.

State and persistence: global card linked list, slot map, ECTCR speed state, proc entry, per-card resources/sysfs attributes, loader buffers, and claimed/ops state. Hardware interrupt and address windows are configured; nothing persists across reboot.

Dependencies and integration points: depends on IOMD, IRQ core, driver core bus APIs, procfs, ARM MM/TLB helpers, ecard assembly loader, and RiscPC memory map.

Risks: explicitly trusts card vendor loader code. Interrupt lockup detection masks the parent interrupt after repeated unrecognized events. Probe/register error path can free cards after partial setup. Slot 8 has special indexed access state. Resource ownership and driver claimed state must stay paired.

Test signals: card detection in proc/sysfs, driver match/probe/remove/shutdown, loader chunk descriptions, EASI/IOC resource mapping, shared backplane interrupt dispatch, and lockup diagnostics with bad IRQ sources.
