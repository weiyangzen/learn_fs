# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.h

## Purpose
This header declares the public VSC transport API and command IDs shared by the SPI transport, firmware loader, and MEI platform adapter.

## Important APIs, types, and functions
It defines command values `VSC_TP_CMD_WRITE`, `VSC_TP_CMD_READ`, `VSC_TP_CMD_ACK`, `VSC_TP_CMD_NACK`, and `VSC_TP_CMD_BUSY`, forward-declares `struct vsc_tp`, declares callback type `vsc_tp_event_cb_t`, and prototypes ROM transfer, normal transfer, event registration, interrupt control, reset, read-needed query, and firmware init functions.

## Control flow and state
There is no implementation flow in the header. Consumers call `vsc_tp_register_event_cb()` to subscribe to transport events, `vsc_tp_xfer()` for normal framed commands, `vsc_tp_rom_xfer()` during firmware loading, and interrupt/reset helpers around MEI state transitions.

## State and persistence behavior
No state is defined beyond opaque pointer ownership and callback signatures. Actual transport state lives in `vsc-tp.c`.

## Dependencies and integration points
It depends only on `linux/types.h` and is included by `vsc-tp.c`, `vsc-fw-loader.c`, and `platform-vsc.c`. Exported functions use the `VSC_TP` namespace in implementations.

## Risks and test signals
Risks are API contract drift between the transport and platform MEI adapter, especially around callback context, IRQ-control balance, and transfer buffer lengths. Test signals are successful compilation of all VSC modules and runtime MEI-over-VSC traffic using the declared functions.
