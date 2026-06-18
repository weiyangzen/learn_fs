# sources/distributed-fs/ceph-client/include/linux/serial_bcm63xx.h

Purpose: `serial_bcm63xx.h` defines Broadcom BCM63xx UART register offsets and bit masks used by the platform serial driver.

Important APIs/types/functions: Macros cover control (`UART_CTL_REG` and reset, stop bit, bits-per-symbol, parity, loopback, RX/TX enable, baud generator bits), baud word, miscellaneous modem/FIFO threshold/fill register, external input configuration and modem interrupt bits, interrupt mask/status bits for TX/RX/error events, and FIFO data/error bits including `UART_FIFO_ANYERR_MASK`.

Control flow: The driver programs control and baud registers, configures FIFO thresholds, reads modem external inputs, services interrupt status bits, masks/unmasks interrupts, and reads FIFO bytes while checking frame/parity/break error bits.

State and persistence behavior: The header owns no state. The hardware registers retain programmed UART mode, modem outputs, FIFO thresholds, interrupt masks, and baud settings until changed or reset.

Dependencies and integration points: It integrates with the BCM63xx serial driver, platform resource mapping, UART/TTY serial core, and interrupt handling.

Risks: Bit definitions include hardware quirks such as overlapping TX parity shift values in this snapshot. Driver code must use masks consistently and avoid confusing interrupt mask and status halves. FIFO error bits must be consumed with the data byte they describe.

Test signals: Baud programming, RX/TX enable/disable, FIFO reset, interrupt mask/status handling for all TX/RX/error bits, modem input/output, parity/stop-bit settings, loopback mode, and error-byte reporting.
