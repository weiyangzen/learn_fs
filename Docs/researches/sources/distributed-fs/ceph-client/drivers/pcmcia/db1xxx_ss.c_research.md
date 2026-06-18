# sources/distributed-fs/ceph-client/drivers/pcmcia/db1xxx_ss.c

Purpose: Provides PCMCIA socket services for Alchemy Db/Pb1xxx development boards. It handles board-specific card detect, voltage/status interpretation, IRQ setup, reset and buffer control through BCSR registers, and static I/O/attribute/common memory mapping.

Important APIs and functions: Main socket ops are `db1x_pcmcia_configure()`, `db1x_pcmcia_get_status()`, `au1x00_pcmcia_set_io_map()`, and `au1x00_pcmcia_set_mem_map()`. Probe/remove are `db1x_pcmcia_socket_probe()` and `db1x_pcmcia_socket_remove()`. IRQ paths include `db1000_pcmcia_cdirq()`, `db1000_pcmcia_stschgirq()`, `db1200_pcmcia_cdirq()`, and threaded `db1200_pcmcia_cdirq_fn()`.

Control flow: Probe determines board type from BCSR, collects card/insert/status/eject IRQs and physical memory resources, remaps I/O with MIPS port-base adjustment, initializes socket fields, registers IRQs, disables status-change IRQ, and registers the socket. Card detect IRQs queue `SS_DETECT`; DB1200/DB1300 use paired insert/eject interrupts where the active one is disabled and the opposite one enabled after debounce. `set_socket` validates Vcc/Vpp, writes BCSR power/reset/buffer bits, disables STSCHG during reset, waits after reset deassertion, then re-enables STSCHG.

State and persistence: `struct db1x_pcmcia_sock` stores socket number, physical mappings, previous flags, IRQ numbers, insert GPIO, and board type. Hardware state persists in board BCSR PCMCIA registers and interrupt enable state.

Dependencies and integration points: Depends on Alchemy/Db1x00 BCSR APIs, MIPS I/O mapping, GPIO/IRQ APIs, `pccard_static_ops`, and PCMCIA socket core. It integrates with board platform devices that provide named resources.

Risks: Board variants have different voltage-key bit positions and interrupt semantics. IRQ polarity/disable rules are hardware-specific, especially DB1200 level-like insert/eject lines. Vpp/Vcc validation must prevent illegal combinations. I/O mapping subtracts `mips_io_port_base`, which is easy to break if MIPS I/O assumptions change.

Test signals: Probe each supported board variant, insert/eject debounce, STSCHG after reset, Vcc/Vpp programming, reset/buffer enable, static memory and I/O access, suspend/resume no-op behavior, and cleanup on platform remove.
