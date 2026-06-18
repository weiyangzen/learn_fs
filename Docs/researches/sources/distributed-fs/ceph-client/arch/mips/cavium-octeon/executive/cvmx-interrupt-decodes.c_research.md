# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c

## Purpose
Generated helpers that enable selected error interrupt bits for GMX RX, PCS lane/interface, SPI receive, and SPI transmit blocks.

## Important APIs, Types, And Functions
Functions are `__cvmx_interrupt_gmxx_rxx_int_en_enable()`, `__cvmx_interrupt_pcsx_intx_en_reg_enable()`, `__cvmx_interrupt_pcsxx_int_en_reg_enable()`, `__cvmx_interrupt_spxx_int_msk_enable()`, and `__cvmx_interrupt_stxx_int_msk_enable()`.

## Control Flow
Each helper clears pending status by writeback, constructs a model-specific mask, intentionally skips reserved or noisy normal-operation bits, and writes the enable/mask CSR.

## State, Persistence, And Dependencies
State is persistent hardware interrupt-mask configuration. Correctness depends on model-specific register layouts.

## Integration Points
RGMII, SGMII, SPI, and XAUI helpers call these during enable. `cvmx-interrupt-rsl.c` calls the GMX RX helper.

## Risks
Wrong model masks can touch reserved fields or miss errors. Some events are intentionally disabled because packet work handles them or they are noisy.

## Test Signals
Validate mask values per model, injected overflow/jabber/fault/training interrupts, and absence of storms from disabled FCS/length/link-change bits.
