# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsx-defs.h

## Purpose
`cvmx-pcsx-defs.h` defines SGMII/1000BASE-X PCS lane register address helpers and bitfield views for Octeon. It covers per-lane auto-negotiation, link timers, interrupt status/enable, PCS control/status, sync/state, polarity, and miscellaneous GMX/PCS controls.

## Important APIs, Types, and Constants
- Static inline address helpers include `CVMX_PCSX_ANX_ADV_REG`, `ANX_EXT_ST_REG`, `ANX_LP_ABIL_REG`, `ANX_RESULTS_REG`, `INTX_EN_REG`, `INTX_REG`, `LINKX_TIMER_COUNT_REG`, `LOG_ANLX_REG`, `MISCX_CTL_REG`, `MRX_CONTROL_REG`, `MRX_STATUS_REG`, `RXX_STATES_REG`, `RXX_SYNC_REG`, `SGMX_AN_ADV_REG`, `SGMX_LP_ADV_REG`, `TXX_STATES_REG`, and `TX_RXX_POLARITY_REG`.
- Address helpers switch on `cvmx_get_octeon_family()` and vary the block stride, especially CN68XX using a `0x4000` block step while most listed families use `0x20000`.
- `void __cvmx_interrupt_pcsx_intx_en_reg_enable(int index, int block);` is declared for interrupt-enable setup implemented elsewhere.
- Union views include auto-negotiation advertised/partner ability and results, extended status, interrupt status/enable, link timer count, logical analyzer, misc controls, MR control/status, RX/TX state diagnostics, sync status, SGMII advertisement, and polarity.
- Important fields include duplex/pause/remote fault advertisement, link-partner abilities, auto-negotiation completion, reset/restart/loopback/speed controls, sync/link/fault status, GMX enable/PCS mode bits, and lane polarity swaps.

## Control Flow
Unlike the pure register-map headers, this file has inline runtime control flow in every address helper. Each helper switches on the Octeon family and returns a `CVMX_ADD_IO_SEG()` address based on lane `offset` and PCS `block_id`. Consumers then read/write the returned CSR and interpret fields with the unions. Interrupt decode code calls the declared `__cvmx_interrupt_pcsx_intx_en_reg_enable()` helper to clear and enable PCS interrupt sources.

## State and Persistence Behavior
The state is hardware PCS lane state: link negotiation, partner ability, reset/restart bits, fault/sync/interrupt latches, logical analyzer data, timers, GMX enable, and polarity configuration. Values persist in PCS CSRs until reset or driver writes and directly affect link bring-up.

## Dependencies and Integration Points
- Depends on `cvmx_get_octeon_family()`, Octeon family constants such as `OCTEON_CN52XX`, `OCTEON_CN68XX`, `OCTEON_CNF71XX`, `OCTEON_FAMILY_MASK`, `CVMX_ADD_IO_SEG`, fixed-width integers, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c` to configure SGMII/1000BASE-X mode, advertise abilities, reset PCS lanes, wait for reset/link/auto-negotiation completion, and report link state.
- Used by `arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c` to clear and enable PCS interrupt bits.

## Risks
- Address stride is family-specific. A wrong family case or fallback returns a valid-looking CSR address for the wrong lane/block.
- Reset, restart auto-negotiation, loopback, and speed/duplex fields are control-plane sensitive; incorrect writes can drop links or misadvertise capabilities.
- Link and interrupt status often require read/clear/write sequencing. Clearing all bits without preserving masks can hide link faults.
- `offset` and `block_id` are not range checked, so callers must validate interface/lane numbers.
- Endian bitfield branches must match hardware bit numbering for status polling macros such as `CVMX_WAIT_FOR_FIELD64`.

## Test Signals
- SGMII link tests should cover auto-negotiation on/off, forced speed/duplex, link partner ability reporting, reset completion, and link up/down transitions.
- Interrupt tests should verify that PCS interrupt status bits clear and enable as expected through `__cvmx_interrupt_pcsx_intx_en_reg_enable()`.
- Runtime failures include lanes stuck in reset, `an_cpt` never set, link partner abilities read incorrectly, unexpected GMX disable, or link status flapping only on specific Octeon families.
