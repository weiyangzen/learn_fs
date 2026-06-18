# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.c

## Purpose
`mchp_pci1xxxx_gp.c` is the PCI parent driver for Microchip PCI1xxxx GP devices. It enables the PCI function, allocates two auxiliary devices, passes BAR/IRQ metadata to them, and tears them down on remove.

## Important APIs, Types, and Functions
Key pieces are `struct aux_bus_device`, global `gp_client_ida`, `gp_auxiliary_device_release()`, `gp_aux_bus_probe()`, `gp_aux_bus_remove()`, `pci1xxxx_tbl`, and `pci1xxxx_gp_driver`. It creates auxiliary names `gp_otp_e2p` and `gp_gpio`.

## Control Flow
Probe enables the PCI device, allocates parent-private storage, creates the OTP/EEPROM auxiliary device with BAR0 start/end metadata, initializes and adds it, then creates the GPIO auxiliary device, allocates one PCI IRQ vector, records `pdev->irq`, initializes/adds the GPIO child, sets driver data, and enables bus mastering. Error paths uninit auxiliary devices, free IDs, and free wrappers in reverse order.

## State and Persistence
State is per-PCI-device `struct aux_bus_device` containing two wrapper pointers. Auxiliary wrapper lifetime is reference-counted through `auxiliary_device` release, which frees the IDA id and wrapper memory.

## Dependencies and Integration Points
Uses PCI core, auxiliary bus, IDA allocation, IRQ vector allocation, and the shared `mchp_pci1xxxx_gp.h` wrapper metadata. Child drivers bind by auxiliary device names.

## Risks
The code stores `pci_resource_end()` in `region_length`, which semantically looks like an end address rather than a length; children use fixed map lengths, reducing immediate effect. IRQ vector allocation is not explicitly freed in remove. Error labels must preserve auxiliary-device init/uninit pairing.

## Test Signals
Signals are successful binding for listed Microchip device IDs, creation of both auxiliary devices, valid IRQ delivery to GPIO, clean remove without leaks, and correct unwind when auxiliary add or IRQ allocation fails.
