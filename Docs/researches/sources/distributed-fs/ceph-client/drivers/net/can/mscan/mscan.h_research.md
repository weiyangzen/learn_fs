# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.h

## Purpose
`mscan.h` defines register bits, register layout, timing macros, private state, and public helper prototypes for the MSCAN driver.

## Important APIs, Types, And Functions
- `MSCAN_*` macros define control, status, interrupt, TX, acceptance filter, misc, ID, mode, retry, and state bits.
- `struct mscan_regs` describes the packed hardware register map, including PPC MPC5xxx reserved spacing through `_MSCAN_RESERVED_`.
- `BTR0_*` and `BTR1_*` macros encode classic CAN bit timing values.
- `struct tx_queue_entry` tracks hardware TX buffer echo/list metadata.
- `struct mscan_priv` embeds `can_priv` first and stores type, flags, register base, clocks, cached interrupt/status state, TX state, TX queue entries, and NAPI.
- Prototypes expose `alloc_mscandev()`, `register_mscandev()`, and `unregister_mscandev()`.

## Control Flow
The platform driver allocates a netdev with `alloc_mscandev()`, fills `reg_base`, `type`, clocks, and IRQ, then calls `register_mscandev()`. The generic driver uses the register layout and bit macros throughout open, TX, RX, IRQ, and mode transitions.

## State And Persistence
The header defines in-memory per-device state and the hardware register map. It also defines compile-time layout differences under `CONFIG_PPC`, including reserved register gaps and clock-source bit semantics.

## Dependencies And Integration Points
It includes clock and type headers and relies on `CONFIG_PPC` to select MPC5xxx-specific layout definitions. It is shared by `mscan.c` and `mpc5xxx_can.c`.

## Risks And Edge Cases
- Register layout changes under `CONFIG_PPC`; using this header for a non-PPC MSCAN integration would need careful validation.
- `MSCAN_REGION` is defined as `sizeof(struct mscan)`, but the defined register type is `struct mscan_regs`; this macro is not used in the inspected files but looks stale.
- `struct mscan_priv` requires `can_priv` to be first for casts and netdev private assumptions.

## Test Signals
Compile PPC and non-PPC configurations where possible, validate register offsets against hardware documentation, and run sparse/build checks for the stale `MSCAN_REGION` macro.
