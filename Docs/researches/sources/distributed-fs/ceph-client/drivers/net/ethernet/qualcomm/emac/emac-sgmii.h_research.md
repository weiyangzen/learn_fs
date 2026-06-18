<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h

## Purpose
`emac-sgmii.h` defines the interface between the EMAC core/MAC code and the internal SGMII PHY layer.

## Important APIs, Types, and Functions
- `struct sgmii_ops` contains optional `init`, `open`, `close`, `link_change`, and `reset` callbacks.
- `struct emac_sgmii` stores SGMII MMIO base, optional digital-lane MMIO base, IRQ number, atomic decode error count, and selected ops.
- Declares hardware-specific initializers for FSM9900, QDF2432, and QDF2400.
- Declares common entry points used by `emac.c` and MAC/PHY code.

## Control Flow
The header has no runtime control flow. It defines the callback contract used by `emac_sgmii_config()` to bind SoC-specific programming to the generic EMAC lifecycle.

## State and Persistence
State described here lives in `struct emac_adapter::phy`. MMIO mappings and IRQ identity are per-device resources; the decode counter is runtime recovery state.

## Dependencies and Integration Points
Forward declarations avoid direct inclusion of platform and adapter definitions. The header is included by `emac.h`, `emac.c`, and SGMII implementation files.

## Risks and Edge Cases
- Callback members are optional, so dispatchers must keep NULL guards.
- QDF2400/QDF2432 require `digital`; FSM9900 does not, but the type does not encode that distinction.
- Adding a new SoC requires both a new initializer declaration and matching ops selection.

## Test Signals
Build coverage catches declaration drift. Runtime signals are successful probe/open/close/reset through all callback combinations and no NULL dereference when an internal PHY is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.h -->
