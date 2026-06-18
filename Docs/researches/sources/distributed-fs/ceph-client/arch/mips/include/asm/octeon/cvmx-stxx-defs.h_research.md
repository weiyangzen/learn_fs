# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-stxx-defs.h

Purpose: defines SPI4 transmit-side STX CSR addresses and register layouts for arbitration, calendars, interrupts, statistics, backpressure, and transmit control.

Important APIs/types/functions: macros include `CVMX_STXX_ARB_CTL`, `BCKPRS_CNT`, `COM_CTL`, `DIP_CNT`, `IGN_CAL`, `INT_MSK`, `INT_REG`, `INT_SYNC`, `MIN_BST`, indexed `SPI4_CALX`, `SPI4_DAT`, `SPI4_STAT`, `STAT_BYTES_HI/LO`, `STAT_CTL`, and `STAT_PKT_XMT`. `__cvmx_interrupt_stxx_int_msk_enable` is declared. Unions describe arbitration controls, counters, enable controls, DIP/frame error limits, calendar ignore masks, interrupt masks/status/sync, minimum burst, SPI4 calendar/data/status, and statistics.

Control flow: no executable logic is present. SPI4 transmit setup writes calendar and timing registers, enables the interface, configures interrupt masks, and reads/clears statistics and error causes.

State and persistence: all state is hardware CSR state. Packet/byte/backpressure counters are live hardware counters; interrupt status reflects latched transmit faults; calendar/control registers persist until reset.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and endian bitfields. It integrates with `cvmx-spi.h` initialization, the common SPX block, and SRX receive-side definitions.

Risks: `block_id` and calendar offsets are masked and can alias invalid inputs. Transmit calendar parity, DIP settings, minimum burst, and ignored calendar fields must match the external SPI4 peer. Interrupt mask/status/sync field overlap can cause accidental missed or uncleared faults if caller semantics are wrong.

Test signals: hardware tests should verify transmit calendar setup, interface enable, packet/byte counters under traffic, error interrupt injection, and backpressure behavior.
