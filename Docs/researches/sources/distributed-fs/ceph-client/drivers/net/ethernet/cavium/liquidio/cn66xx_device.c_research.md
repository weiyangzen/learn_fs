# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.c

## Purpose
This file implements CN6XXX/CN66XX LiquidIO hardware setup shared with CN68XX. It handles soft reset, PCIe error/MPS/MRRS programming, coprocessor clock/tick conversion, global IQ/OQ register setup, queue register setup, queue enable/disable, BAR1 indexing, interrupt processing, register-address binding, CN66XX function-table setup, and CN6XXX config validation.

## Important APIs, Types, And Functions
Exported/common functions include `lio_cn6xxx_soft_reset()`, `lio_cn6xxx_enable_error_reporting()`, `lio_cn6xxx_setup_pcie_mps()`, `lio_cn6xxx_setup_pcie_mrrs()`, `lio_cn6xxx_coprocessor_clock()`, `lio_cn6xxx_get_oq_ticks()`, global IQ/OQ setup helpers, `lio_cn6xxx_setup_iq_regs()`, `lio_cn6xxx_setup_oq_regs()`, queue enable/disable, BAR1 helpers, `lio_cn6xxx_update_read_index()`, interrupt enable/disable, `lio_cn6xxx_process_interrupt_regs()`, `lio_cn6xxx_setup_reg_address()`, `lio_setup_cn66xx_octeon_device()`, and `lio_validate_cn6xxx_config_info()`. `lio_cn66xx_setup_iq_regs()` and `lio_cn66xx_setup_pkt_ctl_regs()` add CN66XX-specific backpressure and packet-control behavior.

## Control Flow
CN66XX setup maps BAR0/BAR1, initializes the DROQ interrupt-enable lock, installs function pointers into `oct->fn_list`, binds register-list pointers, loads `LIO_210SV` config, and stores the coprocessor clock rate. Device register setup configures PCIe MPS/MRRS, enables PCIe errors, writes global input routing, configures CN66XX packet control and global output registers, and sets a window timeout to avoid host hangs on invalid reads. IQ/OQ setup writes ring DMA addresses/sizes and stores doorbell/count register pointers. Queue enable manipulates global IQ/OQ enable masks; disable clears enable masks, waits for reset indication, resets doorbells/credits, and clears pending packet count/time interrupts. Interrupt processing validates the summary register, logs errors, processes DROQ count/time interrupts, sets generic LiquidIO interrupt status, and clears summary bits.

## State And Persistence
Runtime state is in `struct octeon_cn6xxx`, `oct->fn_list`, register-list pointers, IQ/DROQ structures, `oct->io_qmask`, `oct->droq_intr`, and hardware CSRs. No disk persistence is used. Read-index state uses the initial instruction counter saved in each IQ and handles 32-bit counter rollover.

## Dependencies And Integration Points
It integrates with LiquidIO core structures, CN66XX register macros, PCI config access, BAR mapping helpers, MMIO CSR helpers, DROQ packet checking, spinlocks, and generic interrupt status consumption by the core driver.

## Risks
Queue disable uses XOR to clear enable bits, which toggles bits and assumes masks are currently enabled. Polling reset waits have finite `HZ` loops and limited error reporting. Interrupt processing disables DROQ-specific interrupts under a spinlock when DROQ poll mode is active. PCIe MPS/MRRS values are ORed into DPI/SLI registers without clearing existing fields. Config validation covers queue counts, IQ instruction type, OQ refill threshold, and OQ time interrupt, but other config fields are trusted.

## Test Signals
Test CN66XX probe, BAR mapping failure cleanup, reset success/failure, MPS/MRRS configuration, IQ/OQ enable-disable cycles, DROQ interrupts in interrupt and poll modes, 32-bit instruction-count rollover, invalid config rejection, and traffic under packet/time interrupt coalescing.
