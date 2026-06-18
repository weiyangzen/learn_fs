<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c

### Purpose
Implements the Intel Assabet SA1110 development board machine, including board-control GPIO, flash, LCD/video encoder, MCP/audio reset, Neponset expansion detection, CF power, LEDs, keys, UARTs, and machine descriptor setup.

### Important APIs, Types, And Functions
Exports `SCR_value`, `ASSABET_BCR_frob()`, and `assabet_uda1341_reset()`. Important helpers include `assabet_init_gpio()`, ADV7171 bit-bang routines, codec reset helpers, LCD power/backlight callbacks, `assabet_init()`, `map_sa1100_gpio_regs()`, `get_assabet_scr()`, `fixup_assabet()`, `assabet_uart_pm()`, `assabet_map_io()`, and `assabet_init_irq()`.

### Control Flow
Early fixup temporarily maps SA1100 GPIO registers, reads the system configuration register from GPIO pins, and detects Neponset. Map IO installs standard and board mappings, configures memory timing, and registers UARTs. IRQ init initializes SA1100 IRQs and the Assabet board-control GPIO chip. Machine init configures sleep/pin defaults, optionally registers Neponset, registers fixed regulators/CF, keys, LEDs, LCD, flash, MCP, and PCMCIA.

### State, Persistence, And Dependencies
State includes `SCR_value`, board control register shadowing through a GPIO chip, platform data for flash/LCD/MCP/regulators/keys/LEDs, and static I/O maps. Dependencies include SA1100 generic helpers, GPIO/LED/key/regulator/MTD/MCP/framebuffer subsystems, Neponset support, and machine tags.

### Integration Points
The `MACHINE_START(ASSABET, ...)` descriptor connects common SA1100 map, IRQ, timer, late PM, and restart paths with board-specific fixup and init.

### Risks
The SCR read is early and hardware-specific. Board-control register manipulation must be serialized through the GPIO abstraction. Neponset changes RAM/device behavior before paging. Video encoder bit-banging has timing assumptions.

### Test Signals
Assabet boot with and without Neponset, flash partitions, LCD/backlight, UART PM, CF power, MCP/audio reset, LEDs/keys, and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c -->
