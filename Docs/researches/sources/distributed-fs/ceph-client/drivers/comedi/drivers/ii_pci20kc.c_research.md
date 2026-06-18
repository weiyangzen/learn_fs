## sources/distributed-fs/ceph-client/drivers/comedi/drivers/ii_pci20kc.c

### Purpose
`ii_pci20kc.c` is a legacy memory-mapped Comedi driver for Intelligent Instruments PCI-20001C carrier boards and up to three add-on modules. It supports carrier DIO on -2A boards, PCI-20006M AO modules, and PCI-20341M AI modules.

### Important APIs, Types, And Functions
The file defines carrier/module ID values, module register maps, `ii20k_ao_ranges`, `ii20k_ai_ranges`, and key callbacks `ii20k_init_module()`, `ii20k_ao_insn_write()`, `ii20k_ai_setup()`, `ii20k_ai_insn_read()`, `ii20k_dio_config()`, DIO insn handlers, `ii20k_attach()`, and `ii20k_detach()`.

### Control Flow
Attach validates a manually supplied memory base, reserves and maps 0x400 bytes, reads the carrier ID to determine DIO availability and module-empty bits, then allocates four subdevices: one per module slot and one carrier DIO subdevice. Module initialization switches on the module ID and configures AO, AI, or unused. AO writes offset-munged 16-bit values LSB/MSB then strobes. AI initializes the module for software conversion, programs gain-dependent settling timing and chanlist, triggers conversion through a pacer-reset read, waits for interrupt flag clear, reads LSB/MSB, and converts two's-complement to offset binary. DIO configures full 8-bit ports as input or output and writes only changed ports.

### State, Persistence, And Dependencies
Persistent state is the manually reserved memory region, MMIO mapping, subdevice module layout, per-AO readback, and DIO `io_bits`/state. It depends on fixed carrier slot offsets, Comedi legacy config, Comedi range munger helpers, and byte MMIO ordering.

### Integration Points
The driver uses `module_comedi_driver()` rather than PCI auto-detection, despite the PCI name. It integrates module identity bits into Comedi subdevice discovery.

### Risks
Manual memory-base configuration is fragile and limited to the driver's hard-coded address mask. Module probing trusts register IDs. DIO port configuration is coarse-grained by 8-bit port. In `ii20k_dio_config()`, `ctrl23` receives both `II20K_CTRL01_SET` and `II20K_CTRL23_SET`, which looks suspicious but may match hardware bit layout.

### Test Signals
Test invalid and conflicting memory bases, both carrier IDs, empty and populated slots for all supported module IDs, AO readback, AI gains/timing, DIO per-port direction changes, detach unmap/release, and unknown module IDs becoming unused subdevices.
