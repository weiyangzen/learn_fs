# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_uart.h

**Purpose:** Declares BCM63xx UART platform registration.

**Important APIs/types/functions:** Exports `bcm63xx_uart_register(unsigned int id)`.

**Control flow:** Board setup registers UART instances by ID, and the implementation maps ID to the correct register set/IRQ from CPU tables.

**State and persistence behavior:** No header state. Registration creates serial platform device state and console resources.

**Dependencies and integration points:** Integrated by BCM63xx board setup, serial driver, console/early console path, CPU register and IRQ tables.

**Risks:** Registering an ID absent on a SoC can point at `UART1` placeholder resources. Console availability is sensitive to registration order and clock/frequency setup.

**Test signals:** Boot with console on UART0 and UART1 where present, verify baud rate, interrupts, early/late console handoff, and invalid-ID handling.
