# sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.c

Purpose: Implements Broadcom BCM63xx PCMCIA/CardBus socket services. It registers either a platform socket driver or, with CardBus enabled, a PCI CardBus bridge shim that then registers the platform driver. It handles register programming, card detection, card type/voltage inference, static memory mapping, and polling-based event delivery.

Important APIs and functions: The socket ops are `bcm63xx_pcmcia_sock_init()`, `bcm63xx_pcmcia_suspend()`, `bcm63xx_pcmcia_get_status()`, `bcm63xx_pcmcia_set_socket()`, `bcm63xx_pcmcia_set_io_map()`, and `bcm63xx_pcmcia_set_mem_map()`. Probe/remove are `bcm63xx_drv_pcmcia_probe()` and `bcm63xx_drv_pcmcia_remove()`. CardBus-specific registration uses `bcm63xx_cb_probe()`, `bcm63xx_cb_exit()`, and a Broadcom PCI id table.

Control flow: Probe validates platform memory resources and IRQ/platform data, maps the controller registers and I/O window, fills `struct pcmcia_socket` with static resource ops and features, initializes control/timing registers, registers the socket, and starts a timer. The timer reads current status, computes changed bits masked by `requested_state.csc_mask`, calls `pcmcia_parse_events()`, and reschedules. New card detection toggles VS output-enable combinations, samples VS/CD pins, indexes `vscd_to_cardtype`, and enables PCMCIA or CardBus logic.

State and persistence: Runtime state lives in `struct bcm63xx_pcmcia_socket`: mapped registers, resources, card type, card-detected flag, previous status, requested socket state, timer, and static memory resources. Hardware state persists in BCM63xx PCMCIA control/timing registers while the driver is loaded.

Dependencies and integration points: Depends on BCM63xx register access, platform resources, GPIO ready line, Linux PCI if CardBus is enabled, `pccard_static_ops`, and the PCMCIA socket core.

Risks: Hardware cannot control socket power, so status always reports `SS_POWERON`; this can confuse generic power assumptions. Card-type inference depends on electrical settling and table coverage. Remove does not explicitly call `pcmcia_unregister_socket()` in the shown path, which is a lifecycle point to inspect against surrounding kernel version expectations. CardBus reset polarity is inverted for detected CardBus cards.

Test signals: Probe on BCM63xx with and without CardBus, insertion/removal polling, VS/CD card-type classification, ready GPIO behavior, reset assertion/deassertion, static common/attribute memory mapping, and module unload/removal cleanup.
