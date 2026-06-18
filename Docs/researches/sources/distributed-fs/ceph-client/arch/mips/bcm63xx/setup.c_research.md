# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/setup.c

Purpose: BCM63xx architecture setup hook for machine restart/halt, memory setup, board setup, device registration, and core platform init.

Important APIs and functions: key functions include bcm63xx_machine_halt, bcm6348_a1_reboot, bcm63xx_machine_reboot, __bcm63xx_machine_reboot, plat_time_init, plat_mem_setup, bcm63xx_register_devices. These functions expose early architecture services or small platform controllers to the rest of the BCM63xx port.

Control flow: called from MIPS platform hooks, board initialization, or generic kernel subsystems depending on boot stage. Hardware access is direct MMIO through BCM63xx register helpers.

State and persistence: maintains only boot/runtime kernel state such as global parsed NVRAM data, GPIO/chip-select/timer register state, platform callbacks, or early-console output. Flash contents are read but not rewritten here unless the underlying hardware state is explicitly toggled.

Dependencies and integration points: includes linux/init.h, linux/kernel.h, linux/delay.h, linux/memblock.h, linux/ioport.h, linux/pm.h, asm/bmips.h, asm/bootinfo.h, asm/time.h, asm/reboot.h; integration is with BCM63xx CPU detection, register maps, generic MIPS boot hooks, GPIO/IRQ/timer/serial subsystems, and board code.

Risks and test signals: these files sit early in boot, so bad register offsets or CPU-family assumptions can hang before full logging. Test with early console, boot logs, `/proc/iomem`, GPIO/chip-select behavior, board detection, and subsystem-specific smoke tests.
