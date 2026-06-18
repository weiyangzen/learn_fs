# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_uart.c

- Purpose: Configures the Mantis UART used for IR remote scancode reception and schedules bottom-half decoding from IRQ1.
- Important APIs/types/functions: `mantis_uart_init()`, `mantis_uart_exit()`, internal `mantis_uart_setup()`, `mantis_uart_work()`, and `mantis_uart_read()`.
- Control flow: Init disables UART RX interrupt, programs parity/baud and byte threshold, flushes RX, enables hardware and IRQ1, and schedules an initial drain. IRQ1 masks itself and schedules work; the worker drains FIFO until empty or timeout, emits scancodes via input code, then unmasks IRQ1. Exit masks interrupt, disables UART RX interrupt, and flushes work.
- State and persistence: Uses `uart_work`, board UART parameters, and rc device in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Depends on Mantis MMIO registers, interrupt mask helpers, and `mantis_input_process()`.
- Risks: Scancode assembly masks data to 6 bits per byte and treats status bits as frame/parity errors. The 10 ms drain budget may leave data if FIFO remains busy. Correct input teardown must occur after UART work is flushed.
- Test signals: Test IR key reception, parity/framing error handling, FIFO-full logs, IRQ masking/unmasking, and unload during incoming UART data.
