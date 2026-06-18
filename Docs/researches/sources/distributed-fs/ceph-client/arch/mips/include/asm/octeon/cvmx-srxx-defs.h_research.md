# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-srxx-defs.h

Purpose: defines SPI4 receive-side SRX CSR addresses and register layouts.

Important APIs/types/functions: macros include `CVMX_SRXX_COM_CTL`, `CVMX_SRXX_IGN_RX_FULL`, indexed `CVMX_SRXX_SPI4_CALX`, `CVMX_SRXX_SPI4_STAT`, `CVMX_SRXX_SW_TICK_CTL`, and `CVMX_SRXX_SW_TICK_DAT`. Unions include `cvmx_srxx_com_ctl`, `cvmx_srxx_ign_rx_full`, `cvmx_srxx_spi4_calx`, `cvmx_srxx_spi4_stat`, `cvmx_srxx_sw_tick_ctl`, and `cvmx_srxx_sw_tick_dat`.

Control flow: receive initialization code programs calendar entries, enables the interface and status tracking, configures ignored full conditions, reads calendar/status fields, and can inject software tick control/data values. No functions execute in this header.

State and persistence: state lives in SRX hardware CSRs. Calendar entries and interface-enable bits persist until reset/reconfiguration; status and tick data reflect live receive hardware.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG`. It pairs with `cvmx-stxx-defs.h` for transmit-side SPI4 and `cvmx-spxx-defs.h` for common SPX control during `cvmx-spi` initialization.

Risks: `block_id` and calendar offsets are masked, so invalid values alias. Calendar parity and port fields must match the peer SPI4 calendar or receive synchronization fails. There are no helper functions enforcing proper enable/order sequencing.

Test signals: SPI4 receive link tests should verify calendar programming, `inf_en`/`st_en` behavior, receive-full handling, status length/m fields, and software tick diagnostics.
