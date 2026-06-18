# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gp.h

## Purpose
`mchp_pci1xxxx_gp.h` defines the shared auxiliary-device wrapper used by the PCI parent and Microchip PCI1xxxx child drivers.

## Important APIs, Types, and Functions
`struct gp_aux_data_type` carries `irq_num`, `region_start`, and `region_length`. `struct auxiliary_device_wrapper` embeds `struct auxiliary_device aux_dev` and the shared `gp_aux_data` payload.

## Control Flow
The PCI parent fills the wrapper before auxiliary device registration. Child probe functions recover the wrapper with `container_of()` and read `gp_aux_data`.

## State and Persistence
The wrapper persists for the auxiliary device lifetime. Its release is implemented in the parent C file.

## Dependencies and Integration Points
Includes Linux spinlock, mutex, kthread, types, and auxiliary bus headers. It is the contract between `mchp_pci1xxxx_gp.c`, `mchp_pci1xxxx_gpio.c`, and `mchp_pci1xxxx_otpe2p.c`.

## Risks
The name `region_length` implies a length but the parent fills it from `pci_resource_end()`. Child drivers currently ignore it in favor of fixed sizes, but future users could misinterpret it.

## Test Signals
Signals are correct child `container_of()` recovery, valid BAR and IRQ metadata, and no lifetime bugs when auxiliary devices are removed.
