# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.h

## Purpose
`ixgbe_dcb_82598.h` declares 82598-specific DCB register bit definitions and function prototypes. It is the hardware contract used by the 82598 DCB implementation to program arbitration, PFC, packet-buffer division, and stats mapping.

## Important APIs, Types, And Functions
- Register constants cover DPMCS, RUPPBMR, RT2CR, RDRXCTL, TDTQ2TCCR, TDPT2TCCR, PDPMCS, DTXCTL, buffer-size defaults, and RDRXCTL receive threshold behavior.
- Prototypes expose PFC configuration, RX arbiter configuration, TX descriptor arbiter configuration, TX data arbiter configuration, and aggregate DCB hardware configuration for 82598.

## Control Flow
Generic DCB dispatch includes this header and calls these functions when `hw->mac.type` is `ixgbe_mac_82598EB`. The `.c` implementation uses the bit shifts and masks here to compose MMIO register values from generic credit and priority arrays.

## State And Persistence
The header defines no state. Its constants describe hardware register fields that persist in the adapter until reset or reprogramming. The prototypes represent direct MMIO-mutating operations.

## Dependencies And Integration Points
This header is paired with `ixgbe_dcb_82598.c` and included by `ixgbe_dcb.c` and `ixgbe_dcb_nl.c`. It depends on generic ixgbe hardware definitions being available through includers.

## Risks
- Incorrect shifts or masks will misprogram hardware credits or priority mode and may cause bandwidth, PFC, or TX/RX stalls.
- Constants with names shared with 82599 headers, such as `IXGBE_RDRXCTL_MPBEN`, must stay compatible with each MAC family or be isolated.
- Function signatures must match the generic dispatch expectations; 82598 lacks `prio_tc` arguments used by 82599-family hardware.

## Test Signals
Build coverage for 82598 DCB paths, register readback after DCB setup, traffic-class bandwidth validation, PFC pause behavior, and reset/reapply testing are appropriate signals.
