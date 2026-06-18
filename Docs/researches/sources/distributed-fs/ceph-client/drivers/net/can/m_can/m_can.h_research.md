# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.h

## Purpose
`m_can.h` defines the common data structures and exported interfaces for the Bosch M_CAN class driver and its bus-specific wrappers.

## Important APIs, Types, And Functions
- `enum m_can_lec_type` names M_CAN last-error-code values used by common error reporting.
- `enum m_can_mram_cfg` indexes Message RAM regions: standard filters, extended filters, RX FIFO 0/1, RX buffers, TX event FIFO, and TX buffers.
- `struct mram_cfg` stores offset and element count for each Message RAM region.
- `struct m_can_ops` is the wrapper transport interface for register access, FIFO access, optional wrapper init/deinit, and interrupt clearing.
- `struct m_can_tx_op` carries queued peripheral TX work.
- `struct m_can_classdev` embeds `can_priv`, offload/NAPI, netdev/device pointers, clocks, reset, transceiver, operations, PM flags, interrupt/coalescing state, TX state, MRAM layout, hrtimer, and wake pinctrl.
- Function prototypes expose allocation, free, registration, unregister, clock discovery, MRAM checking, and suspend/resume helpers.

## Control Flow
Wrappers include this header, allocate a private object whose first member is `struct m_can_classdev` or whose netdev private area begins with compatible storage, fill fields such as `ops`, `dev`, `net->irq`, clock frequency, `is_peripheral`, and PM flags, then call `m_can_class_register()`. The common core later calls back into `m_can_ops` for all hardware access.

## State And Persistence
The header lays out all common runtime state. Important cached state includes `active_interrupts`, coalescing parameters, `tx_fifo_putidx`, `tx_fifo_in_flight`, queued `tx_ops`, `tx_peripheral_submit`, and parsed MRAM layout. There is no persistence outside kernel memory and hardware registers.

## Dependencies And Integration Points
The header includes many Linux kernel dependencies used by both common and wrapper code, including CAN core/dev/rx-offload, clk, reset, freezable workqueues, hrtimers, IO, netdevice, PHY, pinctrl, PM runtime, slab, and uaccess. It is the key ABI between `m_can.c`, `m_can_platform.c`, `m_can_pci.c`, and `tcan4x5x-core.c`.

## Risks And Edge Cases
- Because wrappers depend on `container_of()` around `struct m_can_classdev`, private structs must keep layout assumptions consistent.
- `m_can_ops` read/write callbacks return mixed conventions: register read returns `u32`, writes and FIFO access return `int`; common code assumes FIFO errors are propagated.
- `active_interrupts`, TX counters, and workqueue fields are shared across IRQ, NAPI, TX, and close paths, so locking rules in the C file are part of this header contract.

## Test Signals
Compile all wrappers against the header, run sparse/build checks for function pointer signatures, and test both `is_peripheral` and non-peripheral paths because the same structure fields are interpreted differently.
