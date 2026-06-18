# sources/distributed-fs/ceph-client/arch/mips/lantiq/early_printk.c

Purpose: implements early console output for Lantiq ASC UARTs through `prom_putchar`.

Important APIs/functions: `prom_putchar(char c)` waits for the ASC TX FIFO to empty, optionally emits carriage return before newline, and writes a byte to the transmit buffer. Register addresses account for endianness.

Control flow: disables local IRQs, polls `LTQ_ASC_FSTAT`, writes `\r` for `\n`, writes the character, and restores IRQ state.

State and persistence: stateless except for hardware UART FIFO state.

Dependencies and integration: used by generic early printk paths when `CONFIG_EARLY_PRINTK`; depends on `LTQ_EARLY_ASC` and `ltq_r32/ltq_w8`.

Risks: busy-wait can hang if the UART base is wrong or hardware is wedged. It assumes early MMIO mappings and no locking beyond IRQ masking.

Test signals: early boot characters before full console init and correct CRLF handling on serial terminals.
