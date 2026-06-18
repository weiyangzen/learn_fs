# sources/distributed-fs/ceph-client/drivers/pcmcia/soc_common.c

Purpose: Implements common PCMCIA socket services for integrated SoC controllers. It bridges low-level board/SoC operations to the PCMCIA core, handling resource windows, GPIO/regulator controls, status polling/IRQs, map timing, cpufreq integration, and debug/status sysfs.

Important APIs and functions: Exports `soc_pcmcia_regulator_set()`, `soc_common_pcmcia_get_timing()`, `soc_pcmcia_request_gpiods()`, `soc_common_cf_socket_state()`, `soc_pcmcia_init_one()`, `soc_pcmcia_add_one()`, and `soc_pcmcia_remove_one()`. Core PCMCIA ops are `soc_common_pcmcia_sock_init()`, `soc_common_pcmcia_suspend()`, `soc_common_pcmcia_get_status()`, `soc_common_pcmcia_set_socket()`, `soc_common_pcmcia_set_io_map()`, and `soc_common_pcmcia_set_mem_map()`.

Control flow: `soc_pcmcia_add_one()` claims fixed resources, remaps I/O space, installs default timing, initializes low-level hardware and IRQ/GPIO state, sets static-map PCMCIA capabilities, registers cpufreq notifier, registers the socket, and creates a status file. Status events are detected by IRQs and a periodic timer; `soc_common_check_status()` compares current status against prior status and `csc_mask`, then calls `pcmcia_parse_events()`. Socket/map setters update board hardware, optional reset/bus-enable GPIOs, IRQ type, timing arrays, and map translations.

State and persistence: Per-socket state includes requested card-services state, last status, resource objects, speed arrays, status GPIOs/IRQs, reset/bus-enable GPIOs, regulators, clock, poll timer, and cpufreq notifier. Hardware state persists in board-specific registers, GPIOs, regulators, and SoC memory-controller timing registers.

Dependencies and integration points: Depends on `struct pcmcia_low_level` from PCMCIA SoC headers, `pccard_static_ops`, Linux resource, GPIO descriptor, regulator, clock, IRQ, timer, and cpufreq APIs. Used by PXA2xx, SA11xx, and SA1111 drivers.

Risks: This is the central state machine for many board drivers. It mixes IRQ and polling paths, uses `status_lock` for status updates, and toggles IRQ type for card IRQs based on `state->io_irq`. Resource cleanup must mirror add error paths. Low-level `configure_socket()` failure attempts rollback to prior state, which can itself fail. GPIO active-low handling is special for card-detect.

Test signals: Socket registration/removal on all SoC users, IRQ and polling event delivery, sysfs status readability, map translation for I/O/memory/attribute windows, regulator Vcc changes, reset/bus-enable GPIO changes, suspend/resume, and cpufreq timing recalculation.
