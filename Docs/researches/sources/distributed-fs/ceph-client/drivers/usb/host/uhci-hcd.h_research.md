# sources/distributed-fs/ceph-client/drivers/usb/host/uhci-hcd.h

## Purpose
`uhci-hcd.h` is the shared private ABI for the UHCI driver. It defines UHCI register offsets and bit fields, host-controller pointer encoding, TD/QH hardware descriptors, skeleton queue layout, root-hub state machine values, the `struct uhci_hcd` controller state, per-URB state, register accessors for PCI/MMIO/ASpeed/big-endian variants, and descriptor endian conversion helpers.

## Important APIs, Types, And Functions
Key register constants include `USBCMD`, `USBSTS`, `USBINTR`, `USBFRNUM`, `USBFLBASEADD`, `USBSOF`, and `USBPORTSC*`. Link pointer helpers (`UHCI_PTR_TERM`, `UHCI_PTR_QH`, `UHCI_PTR_DEPTH`, `LINK_TO_QH()`, `LINK_TO_TD()`) encode schedule addresses. `struct uhci_qh` represents both endpoint queues and skeleton queues, including hardware link/element fields and software queue, period, phase, load, state, and toggle flags. `struct uhci_td` represents UHCI transfer descriptors. `struct uhci_hcd` is the complete controller state and bus-glue callback table. Inline register functions abstract IO-port, MMIO, big-endian, and ASpeed register maps. `cpu_to_hc32()` and `hc32_to_cpu()` abstract descriptor endianness.

## Control Flow
The header enables the rest of the driver to treat PCI and non-PCI UHCI similarly. Queue code allocates and links `struct uhci_qh`/`struct uhci_td`; core code uses `uhci_readw()`/`uhci_writew()` for hardware control; hub code uses port bit constants; bus glue fills callback pointers and quirk flags in `struct uhci_hcd`. The skeleton queue numbering determines how interrupt, async, ISO, unlinking, and terminating queues are inserted into the hardware schedule.

## State And Persistence Behavior
No durable state is defined. The structures describe runtime state that exists while an HCD instance is alive. Descriptor fields are DMA-visible and can be asynchronously changed by hardware, which is why `qh_element()` and `td_status()` use `READ_ONCE()`. Software state tracks QH lifecycle (`IDLE`, `UNLINKING`, `ACTIVE`), root-hub lifecycle, bandwidth load, FSBR activity, and platform quirks.

## Dependencies And Integration Points
The header depends on Linux USB, list, clock, reset-control, endian, MMIO, and optional IO-port support. It is consumed by all UHCI implementation files. It supports PCI, generic platform, ASpeed, and GRLIB-style endian variations, so configuration macros strongly affect compiled accessors.

## Risks And Edge Cases
The non-PCI accessor block contains several configuration-sensitive paths; incorrect `CONFIG_HAS_IOPORT`/`HAS_IOPORT` combinations or missing big-endian flags would produce bad register access. ASpeed uses a nonstandard register map translated by `uhci_aspeed_reg()` and warns on unsupported registers. Hardware-updated descriptor fields require careful memory ordering and one-time reads. Skeleton queue constants are semantic; mistakes in queue placement affect bandwidth and traversal order.

## Test Signals
Static build coverage across endian/MMIO/PCI/ASpeed options is critical. Runtime signals include correct register access, valid DMA descriptor endianness, stable frame list traversal, proper QH state transitions, accurate root-port count, and no sparse/endian warnings around `__hc32` conversions.
