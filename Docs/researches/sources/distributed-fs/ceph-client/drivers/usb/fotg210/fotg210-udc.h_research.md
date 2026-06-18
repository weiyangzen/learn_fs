# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210-udc.h

## Purpose
`fotg210-udc.h` is the register and private-state header for the FOTG210 gadget/device-controller driver. It names device-side MMIO offsets and bit fields, defines endpoint/request/controller structures, and provides the `gadget_to_fotg210()` conversion helper used by the UDC implementation.

## Important APIs, Types, and Functions
The register constants cover global interrupt masking (`FOTG210_GMIR`), device main control (`FOTG210_DMCR`), address/test/PHY state, control endpoint FIFO/status (`FOTG210_DCFESR`, `FOTG210_CXPORT`), interrupt masks and sources (`FOTG210_DMIGR`, `DMISGR*`, `FOTG210_DIGR`, `DISGR*`), zero-length packet status, endpoint max-packet/stall registers, endpoint-to-FIFO maps, FIFO configuration/count/reset, and DMA registers (`FOTG210_DMATFNR`, `FOTG210_DMACPSR1`, `FOTG210_DMACPSR2`). The private types are `struct fotg210_request`, `struct fotg210_ep`, and `struct fotg210_udc`.

## Control Flow
The header does not execute code directly. `fotg210-udc.c` uses the constants to initialize the device block, mask/unmask interrupt sources, configure endpoints, map FIFOs, start/abort DMA, acknowledge setup/control/data events, and process USB reset/suspend/resume. The structure definitions determine how endpoint queues, stall state, descriptors, EP0 internal state, PHY references, and the bound gadget driver are stored during all UDC callbacks.

## State and Persistence Behavior
All state defined here is runtime-only. `struct fotg210_request` wraps a gadget request with queue linkage. `struct fotg210_ep` persists endpoint configuration and request queue while the gadget is active. `struct fotg210_udc` persists controller-wide lock, MMIO, IRQ trigger metadata, device/core/PHY pointers, gadget object, driver pointer, endpoint table, and EP0 bookkeeping. Hardware state corresponding to the register macros is reset or reprogrammed by probe/start/stop and endpoint enable/disable paths.

## Dependencies and Integration Points
The header depends on kernel USB gadget types, USB PHY types, Linux lists and spinlocks, and MMIO access in the C file. It integrates with the shared `struct fotg210` core through the UDC state backpointer, with gadget function drivers through `struct usb_gadget` and `struct usb_ep`, and with platform hardware through the register map. It is private to the FOTG210 UDC implementation rather than a public kernel API.

## Risks
Bitfield macros are hardware-facing and many compose shifted endpoint/FIFO numbers. Incorrect masking or endpoint numbering can silently program the wrong FIFO, direction, DMA target, or stall bit. `FOTG210_MAX_NUM_EP` and `FOTG210_MAX_FIFO_NUM` fix the implementation at EP0-EP4 and FIFO0-FIFO3/4 semantics; hardware variants with more endpoints need coordinated C changes. Some macros encode field values with shifts that depend on operator precedence, so changes should preserve parentheses carefully.

## Test Signals
Any change should be validated by endpoint configuration tests covering each EP1-EP4 direction and transfer type, FIFO map readback where possible, EP0 setup traffic, DMA target selection for control and data FIFOs, interrupt mask/unmask behavior, and stall/wedge/clear-halt behavior. Compile checks should include the UDC as built-in and module.
