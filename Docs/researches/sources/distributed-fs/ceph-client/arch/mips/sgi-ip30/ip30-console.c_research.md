# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-console.c

Purpose: early IP30 console output through the BaseIO IOC3 UART.

Important APIs and control flow: `console_uart()` uses the fixed XKPHYS IOC3 address `0x900000001f600000` and returns UART A. `prom_putchar()` polls line-status THR-empty with `cpu_relax()` and writes the byte.

State, persistence, and integration: no persistent state; it performs direct MMIO writes before full device setup. Dependencies include the BaseIO IOC3 fixed address and early mapped access. Risks include blocking forever if IOC3 is absent or status never changes, and hard-coded UART A. Test signals are early printk characters on IP30 serial console.
