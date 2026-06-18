# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.h

## Purpose
`ixgbe_dcb_82599.h` defines 82599-family DCB register masks, shifts, and programming entry points. It covers receive/transmit UP-to-TC mapping, RX and TX packet/descriptor arbitration, PFC-related behavior, and DCB-specific TX buffer inter-frame gap constants.

## Important APIs, Types, And Functions
- Constants cover `RTTDCS`, `RTRUP2TC`, `RTTUP2TC`, `RTRPT4C`, `RDRXCTL`, `RTRPCS`, `RTTDT2C`, `RTTPT2C`, `RTTPCS`, and `SECTXMINIFG` DCB fields.
- Prototypes declare PFC configuration, RX arbiter configuration, TX descriptor arbiter configuration, TX data arbiter configuration, and aggregate DCB hardware configuration for 82599-family devices.
- Function signatures include `prio_tc` where hardware needs priority-to-traffic-class mapping.

## Control Flow
Generic DCB code includes this header and calls its prototypes for 82599, X540, X550, X550EM_x, and x550em_a. The implementation composes MMIO register values from generic credit arrays and priority maps using these masks and shifts.

## State And Persistence
The header itself stores no state. It defines the register-field contract for persistent hardware configuration that remains active until reset or later DCB programming.

## Dependencies And Integration Points
It is paired with `ixgbe_dcb_82599.c` and included by generic DCB and DCBNL sources. It relies on ixgbe register base macros from the broader driver headers.

## Risks
- Bitfield mistakes affect hardware arbitration or PFC behavior globally for 82599-family devices.
- Shared macro names with 82598 headers require attention to include order and matching register semantics.
- The `prio_tc` API difference from 82598 is important for IEEE/CEE DCB correctness.

## Test Signals
Compilation across all 82599-family MAC types, DCB register readback, IEEE ETS and PFC configuration, UP-to-TC map verification, traffic-class bandwidth tests, and reset/reconfigure loops are the main signals.
