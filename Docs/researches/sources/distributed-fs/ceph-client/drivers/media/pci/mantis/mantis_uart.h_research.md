# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.h

- Purpose: UART register offsets, status bits, baud/parity enums, and lifecycle prototypes for Mantis IR reception.
- Important APIs/types/functions: `MANTIS_UART_CTL/RXD/BAUD/STAT`, RX status bits, `enum mantis_baud`, `enum mantis_parity`, `mantis_uart_init`, `mantis_uart_exit`.
- Control flow: Board configs choose baud/parity/byte count; UART implementation programs the hardware and forwards decoded keys.
- State and persistence: No state; constants configure volatile UART registers.
- Dependencies and integration points: Included by `mantis_common.h`, board configs, and `mantis_uart.c`.
- Risks: Enum ordering must match arrays and hardware setup switch. Parity enum names/order should be checked against register semantics.
- Test signals: Compile plus IR remote hardware tests across boards.
