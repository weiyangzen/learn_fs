# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-gpio-defs.h

## Purpose
`cvmx-gpio-defs.h` maps Octeon GPIO CSRs and their bit layouts. It covers per-pin configuration, pin input/output data, interrupt enable/clear behavior, boot/debug enables, clock generator outputs, QLM-derived GPIO clocks, multicast behavior, and extended GPIO pin enable/configuration registers.

## Important APIs, Types, And Functions
Important address macros include `CVMX_GPIO_BIT_CFGX`, `CVMX_GPIO_XBIT_CFGX`, `CVMX_GPIO_RX_DAT`, `CVMX_GPIO_TX_SET`, `CVMX_GPIO_TX_CLR`, `CVMX_GPIO_INT_CLR`, `CVMX_GPIO_DBG_ENA`, `CVMX_GPIO_BOOT_ENA`, `CVMX_GPIO_CLK_GENX`, `CVMX_GPIO_CLK_QLMX`, `CVMX_GPIO_MULTI_CAST`, and `CVMX_GPIO_PIN_ENA`. The unions expose fields such as output enable, receive XOR, interrupt enable/type, debounce/filter count and select, clock selection/generation, sync selection, output selection, data masks, and special pin enables.

## Control Flow
The header has no code flow. Drivers configure each pin by composing `union cvmx_gpio_bit_cfgx`, then use set/clear CSRs to drive outputs and interrupt clear CSRs to acknowledge events. Clock-related GPIO uses the clock generator and QLM selector registers before a pin is configured to emit that source.

## State And Persistence
State lives in GPIO hardware CSRs. Pin muxing, output enable, filters, interrupt settings, and output latch state persist until changed or reset. Reading `CVMX_GPIO_RX_DAT` observes current pin state rather than maintained software state.

## Dependencies And Integration Points
The definitions require `CVMX_ADD_IO_SEG`, fixed-width integer types, and the kernel/endian bitfield configuration. Board support code, LED/control-plane drivers, management PHY reset code, and boot/debug pin handling use these CSRs. QLM clock fields tie GPIO behavior to high-speed lane clocking.

## Risks
Different Octeon families expose different GPIO counts and bit layouts; the generic, `cn30xx`, `cn52xx`, `cn61xx`, and `cn63xx` union variants must not be mixed blindly. Address macros mask offsets, so invalid pin numbers can target an unintended valid register. Misconfigured `tx_oe`, `rx_xor`, or interrupt type can invert signals or create interrupt storms.

## Test Signals
Test with pin loopback where available, verify set/clear changes the expected bit in `RX_DAT`, check debounce/filter behavior under toggling inputs, confirm interrupt clear semantics, and validate board-specific GPIO consumers such as reset lines, LED outputs, and QLM clock output selection.
