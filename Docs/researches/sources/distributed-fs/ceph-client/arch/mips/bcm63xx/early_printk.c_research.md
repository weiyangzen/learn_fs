# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/early_printk.c

Purpose: early printk backend that writes characters directly to the BCM63xx UART FIFO before the serial driver is ready.

Important APIs and functions: key functions include wait_xfered, prom_putchar. These functions expose early architecture services or small platform controllers to the rest of the BCM63xx port.

Control flow: called from MIPS platform hooks, board initialization, or generic kernel subsystems depending on boot stage. Hardware access is direct MMIO through BCM63xx register helpers.

State and persistence: maintains only boot/runtime kernel state such as global parsed NVRAM data, GPIO/chip-select/timer register state, platform callbacks, or early-console output. Flash contents are read but not rewritten here unless the underlying hardware state is explicitly toggled.

Dependencies and integration points: includes bcm63xx_io.h, linux/serial_bcm63xx.h, asm/setup.h; integration is with BCM63xx CPU detection, register maps, generic MIPS boot hooks, GPIO/IRQ/timer/serial subsystems, and board code.

Risks and test signals: these files sit early in boot, so bad register offsets or CPU-family assumptions can hang before full logging. Test with early console, boot logs, `/proc/iomem`, GPIO/chip-select behavior, board detection, and subsystem-specific smoke tests.
