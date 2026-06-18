# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pcsxx-defs.h

## Purpose
`cvmx-pcsxx-defs.h` defines 10G/XAUI PCS register address helpers and bitfield views for Octeon. It covers block-level 10G PCS control/status, BIST, bit lock, interrupts, logical analyzer, misc controls, receive sync state, supported speed abilities, 10G status, polarity, and TX/RX state diagnostics.

## Important APIs, Types, and Constants
- Static inline address helpers include `CVMX_PCSXX_10GBX_STATUS_REG`, `BIST_STATUS_REG`, `BIT_LOCK_STATUS_REG`, `CONTROL1_REG`, `CONTROL2_REG`, `INT_EN_REG`, `INT_REG`, `LOG_ANL_REG`, `MISC_CTL_REG`, `RX_SYNC_STATES_REG`, `SPD_ABIL_REG`, `STATUS1_REG`, `STATUS2_REG`, `TX_RX_POLARITY_REG`, and `TX_RX_STATES_REG`.
- Helpers switch on `cvmx_get_octeon_family()` and choose a block stride of `0x8000000` for CN52XX/CN56XX or `0x1000000` for CN68XX and the fallback.
- `void __cvmx_interrupt_pcsxx_int_en_reg_enable(int index);` is declared for interrupt setup implemented in the interrupt decode module.
- Union views expose 10G alignment and lane sync (`cvmx_pcsxx_10gbx_status_reg`), BIST, per-lane bit lock, PCS control reset/loopback/speed/low-power, PCS type, interrupt enable/status, logical analyzer options, GMX/XAUI enable and swaps, sync state per lane, 10G speed ability, link/fault status, supported 10G variants, lane polarity, and TX/RX state machine diagnostics.
- CN52XX/CN52XXp1-specific union variants account for reduced or differently defined interrupt/polarity/state fields.

## Control Flow
The executable control flow is in inline address helpers, each selecting the correct CSR base/stride for the active Octeon family. Consumers perform the actual link management: read control/status, write reset or GMX enable bits, poll for reset clear, alignment, receive link, and fault state, then restore interrupt enables.

## State and Persistence Behavior
The header describes hardware state for 10G PCS/XAUI interfaces. It persists in CSRs and controls link reset, loopback, speed, low-power mode, XAUI/GMX enable, lane polarity, alignment, bit lock, receive link, transmit/receive faults, and interrupt latches. Diagnostic state such as sync and TX/RX state-machine fields is transient but globally visible while the link is active.

## Dependencies and Integration Points
- Depends on `cvmx_get_octeon_family()`, Octeon family constants, `CVMX_ADD_IO_SEG`, fixed-width integers, and `__BIG_ENDIAN_BITFIELD`.
- Used by `arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c` to initialize XAUI, save/restore interrupt masks, toggle GMX enable, reset PCS, wait for alignment and link status, clear interrupts, and query link health.
- Used by `arch/mips/cavium-octeon/executive/cvmx-interrupt-decodes.c` for PCSXX interrupt enable setup.

## Risks
- Family stride mistakes send CSR operations to the wrong 10G interface block.
- Link bring-up sequencing relies on correct reset, alignment, receive-link, and fault bits; bitfield drift can cause false link-up or endless wait loops.
- Interrupt enable/status fields differ for CN52XX, so generic code must use the right union variant when enabling masks.
- Polarity and lane-swap controls can make a physical link fail even when higher-level configuration is correct.
- No helper validates `block_id`, so bad interface indexes can access undefined CSR space.

## Test Signals
- XAUI/10G link tests should verify reset completion, alignment (`alignd`), receive link, no transmit/receive faults, lane bit lock, and stable speed ability reporting.
- Interrupt tests should confirm that PCSXX fault bits can be cleared and enabled without losing masks.
- Family-specific hardware or simulator coverage should include CN52XX/CN56XX stride behavior and CN68XX/fallback stride behavior.
- Failure signals include XAUI init timeouts, alignment never asserted, false fault reports, GMX output disabled unexpectedly, or link behavior differing only by Octeon family.
