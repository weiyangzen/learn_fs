# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-isys-csi2-reg.h

## Purpose
This header defines IPU6 ISYS CSI-2 receiver register offsets, interrupt register layouts, PPI/CSI front-end controls, hub controls, generation-specific top IRQ registers, and DPHY timing/control registers.

## Important APIs, Types, And Data
Macros cover per-port base address calculation, port reset/control registers, four IRQ groups per port, error IRQ masks for IPU6 and IPU6SE, FS/FE virtual-channel IRQ bits, PPI2CSI enable/configuration, CSI front-end mode/mux/sync controls, hub reset/access registers, top-level IRQ registers for IPU6 and IPU6V6/MTL, `IPU6_ISYS_UNISPART_IRQ_CSI2(port)`, and SIP/port DPHY timing offsets.

## Control Flow
This file is definition-only. CSI-2 receiver code and ISYS setup use the definitions to initialize receivers, clear/mask/enable interrupts, calculate per-port MMIO bases, and program DPHY timings.

## State And Persistence
No software state is stored here. It describes hardware registers and bit encodings.

## Dependencies And Integration Points
It depends on Linux bit helpers and is included by the IPU6 PCI/ISYS/CSI-2 paths. It must align with the hardware-generation data chosen in `ipu6_internal_pdata_init()`.

## Risks And Test Signals
The IRQ mapping and generation-specific offsets are risk areas: MTL uses different top IRQ addresses and firmware-access offsets. Test signals include CSI receiver probe on each hardware generation, FS/FE IRQ delivery per virtual channel, receiver error reporting, and DPHY timing programming for 2-lane and 4-lane sensors.
