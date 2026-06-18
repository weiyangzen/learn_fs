# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-console.c

Purpose: early console output for IP27 through the IOC3 UART selected by firmware KL console information.

Important APIs and control flow: `console_uart()` chooses `master_nasid` if known or the current NASID, obtains `KL_CONFIG_CH_CONS_INFO(nasid)->memory_base`, casts it to IOC3, and returns UART A registers. `prom_putchar()` polls line-status THR-empty and writes one byte.

State, persistence, and integration: no durable state is stored; it reads KL config and IOC3 MMIO. Dependencies include early KL config validity, `master_nasid`, and IOC3 register layout. Risks include blocking forever if UART status never becomes empty and hard-coded UART A use. Test signals are working early printk output before full serial driver initialization.
