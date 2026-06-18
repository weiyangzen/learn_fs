<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h

Purpose: Defines SB1250 dual-UART register fields for character format, parity, flow control, commands, status, baud-rate programming, input/output pins, interrupts, masks, and full-interrupt timing.

Important APIs/types/functions: Mode macros `V_DUART_BITS_PER_CHAR_*`, `V_DUART_PARITY_MODE_*`, stop-bit and channel-mode flags; command macros `M_DUART_RX_EN`, `M_DUART_TX_EN`, `V_DUART_MISC_CMD_*`; status bits `M_DUART_RX_RDY`, `M_DUART_TX_RDY`, error bits; baud helper `V_DUART_BAUD_RATE`; data masks; input/output pin and change bits; per-channel and combined interrupt status/mask macros; `M_DUART_OUT_PIN_SET/CLR(chan)` and full interrupt control fields.

Control flow: UART code composes mode registers, enables RX/TX, uses `V_DUART_BAUD_RATE` for the divisor, polls status or services interrupts, transfers data through hold registers, and manipulates modem/board pins through output-port macros.

State and persistence: The header describes UART register state: FIFO readiness, line errors, break state, pin changes, interrupt masks, baud divisor, and output latch commands. It owns no software buffers or locking.

Dependencies and integration points: Depends on `sb1250_defs.h` and feature predicates for newer full-interrupt fields. Integrated by early console, serial driver, and board support using SiByte DUART register addresses.

Risks: `V_DUART_BAUD_RATE` assumes a 100 MHz source clock and integer division, so clock changes require care. Reserved bits are documented as must-be-zero in several registers. Interrupt macros have both combined and per-channel forms that can be confused.

Test signals: Serial console boot, baud-rate smoke tests, RX/TX interrupt tests, modem-control pin tests, and allmodconfig/SiByte defconfig builds provide the main signals.

Source read size: 349 lines, 11709 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h -->
