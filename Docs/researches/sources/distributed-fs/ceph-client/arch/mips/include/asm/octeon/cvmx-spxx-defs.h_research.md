# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-spxx-defs.h

Purpose: describes common SPI4/SPX interface CSRs for clocks, deskew, driver strength, error handling, interrupt masks/status, training pattern accounting, and BIST.

Important APIs/types/functions: address macros cover `CVMX_SPXX_BCKPRS_CNT`, `BIST_STAT`, `CLK_CTL`, `CLK_STAT`, `DBG_DESKEW_CTL`, `DBG_DESKEW_STATE`, `DRV_CTL`, `ERR_CTL`, `INT_DAT`, `INT_MSK`, `INT_REG`, `INT_SYNC`, `TPA_ACC`, `TPA_MAX`, `TPA_SEL`, and `TRN4_CTL`, indexed by `block_id`. `__cvmx_interrupt_spxx_int_msk_enable` is declared for interrupt unmasking. Register unions provide fields for backpressure counts, BIST status, DLL/clock training controls, deskew state, CN38XX/CN58XX drive controls, error counters, interrupt causes/masks, TPA counters, and training controls.

Control flow: no logic is implemented beyond address calculation. Drivers program clock/training registers, poll status, enable interrupt masks, and clear or inspect interrupt/status registers via CSR accessors.

State and persistence: all state is SPX hardware state. Counters accumulate until reset/clear by hardware policy. Interrupt masks and training controls persist in CSRs until changed or reset.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and OCTEON endian bitfield conventions. It is used by SPI4 initialization and interrupt code alongside `cvmx-srxx-defs.h`, `cvmx-stxx-defs.h`, and `cvmx-spi.h`.

Risks: `block_id` is masked with `& 1`, so invalid IDs alias silently. Clock/training/deskew fields are timing-sensitive; incorrect writes can prevent link synchronization. CN38XX and CN58XX drive-control layouts differ. Interrupt register, mask, and sync registers carry similar field names but different semantics, so write-one-to-clear versus mask behavior must be checked in callers.

Test signals: hardware bring-up should check BIST, stable clock status bits, successful training, expected interrupt causes under injected SPI errors, and backpressure/TPA counters during traffic.
