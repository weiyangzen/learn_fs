<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h

### Purpose
`ts78xx-fpga.h` defines FPGA ID values and capability structures for Technologic Systems TS-78xx FPGA-attached devices.

### Important APIs, Types, And Functions
It defines `TS7800_FPGA_MAGIC`, `FPGAID()`, enum `fpga_ids`, `struct fpga_device`, `struct fpga_devices`, and `struct ts78xx_fpga_data`.

### Control Flow
There is no executable flow. The header provides data contracts for TS-78xx setup code to identify FPGA revisions and supported devices.

### State, Persistence, And Dependencies
The header has no state. Runtime users store FPGA ID, state, and support flags for RTC, NAND, and RNG devices in `ts78xx_fpga_data`.

### Integration Points
TS-78xx board setup and FPGA probing code include this header to decide which FPGA-backed platform devices are present and initialized.

### Risks
FPGA IDs are externally assigned and the comment warns not to invent or borrow IDs. Misidentifying support flags could register unavailable devices.

### Test Signals
TS-78xx boot should read a known FPGA ID and register only the supported RTC, NAND, and RNG devices for that revision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-fpga.h -->
