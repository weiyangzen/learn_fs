# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ath79/ar933x_uart.h

**Purpose:** Defines the AR933x-specific UART register layout and bit fields. It supports the compact 20-byte UART block used by AR933x platform serial code rather than the more common 8250-compatible layout.

**Important APIs/types/functions:** Exports register offsets `AR933X_UART_DATA_REG`, `CS_REG`, `CLOCK_REG`, `INT_REG`, and `INT_EN_REG`; FIFO/register sizes; data CSR bits; control/status fields for parity, DTE/DCE interface mode, DMA, ready override, break, host interrupt, TX/RX busy; clock step/scale masks; and interrupt bits for RX valid, TX ready, framing/overflow/parity/break, RX full, and TX empty. It relies on `BIT()` being visible through including code and declares no functions.

**Control flow:** Serial drivers use the offsets to poll RX/TX readiness, program parity/interface/flow-control mode, compute fractional clock divisor values, acknowledge interrupt sources, and enable selected interrupts. The header itself is declarative.

**State and persistence behavior:** No software state is stored. Consumers mutate UART FIFO, control, clock, interrupt-status, and interrupt-enable registers. UART configuration persists until reset or reprogramming by serial/console paths.

**Dependencies and integration points:** Integrated by AR933x console/serial code and platform device setup, using the base address from `ar71xx_regs.h`. It sits on the low-level printk/early-console path where missing includes or wrong bit values are visible very early in boot.

**Risks:** `AR933X_UART_CLOCK_STEP_M` is defined twice with the same value; this is harmless to the preprocessor but is a maintenance smell. Missing an include for `BIT()` in a direct consumer would break builds. Wrong clock scale/step programming can produce unusable baud rates, and wrong interrupt masks can lose console input or flood interrupts.

**Test signals:** Compile serial console users with warnings enabled, boot with early console and normal console, verify baud rate accuracy, RX/TX interrupt handling, break/framing/overflow reporting, FIFO limits, and suspend/resume or reset reinitialization.
