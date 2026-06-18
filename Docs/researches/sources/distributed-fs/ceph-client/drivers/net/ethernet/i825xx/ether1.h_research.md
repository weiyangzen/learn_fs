
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.h

## Purpose
`ether1.h` defines private state, register offsets, control bits, and Intel 82586 descriptor/control structures for the Acorn Ether1 driver. Most definitions are visible only when `__ETHER1_C` is defined by `ether1.c`.

## Important APIs, Types, And Functions
- `struct ether1_priv` stores mapped base address, TX/RX ring pointers, bus type, and reset/init flags.
- Register macros include `REG_PAGE`, `REG_CONTROL`, `ETHER1_RAM`, `IDPROM_ADDRESS`, and control bits `CTRL_RST`, `CTRL_LOOPBACK`, `CTRL_CA`, and `CTRL_ACK`.
- Descriptor typedefs include `tdr_t`, `tx_t`, `tbd_t`, `rfd_t`, `rbd_t`, `nop_t`, `mc_t`, `sa_t`, `cfg_t`, `scb_t`, `iscp_t`, and `scp_t`.
- Command/status macros define 82586 commands, SCB command bits, RX/TX status bits, TDR result bits, and configuration byte fields.

## Control Flow
The header does not execute logic but establishes the binary layout used by `ether1.c` when writing structures into card RAM and reading status back from the 82586.

## State And Persistence Behavior
State is represented by `struct ether1_priv` in netdev private memory and by descriptors written to card RAM. The header itself stores no state.

## Dependencies And Integration Points
It is tightly coupled to `ether1.c` via `__ETHER1_C` and `priv(dev)`. It integrates with Intel 82586 hardware layout and Acorn Ether1 register mapping.

## Risks And Edge Cases
- Struct sizes and field order must match 82586 hardware format and the fixed offsets used in `ether1.c`.
- `I82586_NULL` is `-1` and must be written as a 16-bit/offset sentinel where expected.
- Header visibility depends on `__ETHER1_C`, so external reuse is intentionally prevented.

## Test Signals
Successful initialization command statuses, correct TX/RX descriptor parsing, and no RAM layout mismatch warnings during `ether1_init_for_open()` validate this header.
