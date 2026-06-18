# sources/distributed-fs/ceph-client/drivers/pcmcia/electra_cf.c

Purpose: Implements a CompactFlash socket driver for the PA Semi Electra evaluation board. It uses device-tree resources and GPIO registers to provide static PCMCIA mappings, card-detect events, power selection, and IRQ delivery to the PCMCIA core.

Important APIs and functions: Socket ops are `electra_cf_ss_init()`, `electra_cf_get_status()`, `electra_cf_set_socket()`, `electra_cf_set_io_map()`, and `electra_cf_set_mem_map()`. Runtime event functions are `electra_cf_timer()` and `electra_cf_irq()`. Probe/remove are `electra_cf_probe()` and `electra_cf_remove()`.

Control flow: Probe reads two address resources, maps memory and I/O, maps a fixed GPIO controller base, parses card-detect/voltage/power GPIO properties, requests IRQ and address regions, fills static socket fields, registers the socket, marks it active, and starts polling. IRQ and timer both call the timer routine; when presence changes, it queues `SS_DETECT`. `set_socket` treats reset as power-off, maps Vcc to 3.3V or 5V GPIO outputs, and writes GPIO enable/write bits.

State and persistence: `struct electra_cf_socket` stores mapped bases, resource sizes, GPIO numbers, present/active flags, timer, IRQ, and embedded socket. Hardware state persists in GPIO output registers and static mappings.

Dependencies and integration points: Depends on Open Firmware address/IRQ/property parsing, PA Semi/PowerPC I/O helpers, PCMCIA static resource ops, and the generic socket core.

Risks: The GPIO base is hard-coded, and property values are consumed as raw GPIO bit numbers rather than gpiod descriptors. The Vcc switch accepts `5` rather than the core's common `50` decivolt convention, which is a compatibility point to verify. Polling and IRQ both drive the same event path.

Test signals: Device-tree probe, GPIO property validation, card detect IRQ and poll changes, 3.3V/5V power writes, static attribute/common memory offsets, I/O region reservation, and module/platform removal cleanup.
