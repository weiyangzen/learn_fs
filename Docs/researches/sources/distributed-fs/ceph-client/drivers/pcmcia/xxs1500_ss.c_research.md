# sources/distributed-fs/ceph-client/drivers/pcmcia/xxs1500_ss.c

Purpose: Implements PCMCIA socket services for the MyCable XXS1500 MIPS/Au1x00 platform using fixed physical windows and board GPIOs.

Important APIs and functions: The platform driver registers `xxs1500_pcmcia_probe()` and `xxs1500_pcmcia_remove()`. PCMCIA ops are `xxs1500_pcmcia_sock_init()`, `xxs1500_pcmcia_sock_suspend()`, `xxs1500_pcmcia_get_status()`, `xxs1500_pcmcia_configure()`, `au1x00_pcmcia_set_io_map()`, and `au1x00_pcmcia_set_mem_map()`. `cdirq()` handles card-detect IRQs.

Control flow: Probe allocates one socket, reads named platform resources for attribute, memory, and I/O physical areas, remaps I/O and adjusts for `mips_io_port_base`, fills a static-map `pcmcia_socket`, requests a GPIO card-detect IRQ, and registers the socket. Configure supports only Vcc 0 or 3.3V, toggles low-active power, asserts/deasserts reset and buffer-enable on reset changes, and waits 500 ms after deassert. Status reads GPIOs for card detect, voltage key, power, reset/ready, and battery signals.

State and persistence: `struct xxs1500_pcmcia_sock` stores physical windows, adjusted virtual I/O base, embedded socket, and previous flags. Hardware state persists in GPIO outputs and static physical maps.

Dependencies and integration points: Depends on MIPS Au1x00 headers, legacy GPIO API, platform resources, PCMCIA static resource ops, and fixed board wiring.

Risks: The I/O remap arithmetic subtracts `mips_io_port_base` and must be reversed exactly for `iounmap()`. Only 3.3V cards are supported; 5V cards are reported as unsupported. Fixed GPIO numbers make the driver non-portable. Card detect uses only one of two detect GPIOs for IRQ.

Test signals: Platform probe with all three named resources, I/O remap success, card-detect IRQ on GPIO_CDA, status values for present/absent/voltage-key states, 3.3V power/reset sequencing, and clean remove.
