<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h

## Purpose
This header describes the Altera/Intel Arria 10 MAX5 System Resource Chip MFD interface. It defines register addressing helpers, system-controller register constants, valid GPIO ranges for inputs and outputs, and the core `struct altr_a10sr`.

## Important APIs, Types, And Functions
- Address helpers: `WRITE_REG_MASK`, `READ_REG_MASK`, `ALTR_A10SR_REG_OFFSET(X)`, `ALTR_A10SR_REG_BIT(X)`, `ALTR_A10SR_REG_BIT_CHG(X, Y)`, and `ALTR_A10SR_REG_BIT_MASK(X)` model paired even write and odd read registers.
- Register constants cover version read/NOP, LED output, pushbutton/DIP input and IRQ flag clear, power-good registers, FMC/PCIe power enable, HPS reset/warm reset/key, USB/QSPI/file reset, SFP controls, I2C master select, and PMBus.
- Valid ranges distinguish LED/output bits and input pushbutton/DIP bits.
- `struct altr_a10sr` stores the parent device and assigned regmap.

## Control Flow
The MFD core creates a regmap for the MAX5 chip and exposes child devices. GPIO/LED/reset/power child code uses the helper macros to map logical GPIO numbers to paired register offsets and bit positions, handling the chip's even-address write and odd-address read convention.

## State And Persistence
Runtime software state is just the device/regmap pair. Hardware state includes LED outputs, pushbutton/DIP input status, power-good flags, power-enable controls, reset controls, SFP controls, I2C master selection, and PMBus control. Register effects persist in the system-resource chip until overwritten or reset.

## Dependencies And Integration Points
The header includes completion, list, MFD core, regmap, and slab headers for the core implementation context. It integrates with Arria10 board-management child drivers, GPIO/LED/reset consumers, and regmap-backed MFD cells.

## Risks And Edge Cases
- The even-write/odd-read register convention is easy to violate; helpers should be used consistently.
- `ALTR_A10SR_REG_BIT_CHG(X, Y)` shifts `X` by the bit position for `Y`; callers must pass a value already constrained to the intended bit width.
- Valid input/output ranges are not enforced by macros, so child drivers must reject unsupported GPIO numbers.
- Reset and power-enable registers can disrupt the board when written incorrectly.

## Test Signals
Verify regmap probe, version read, LED writes with matching odd-address readback, pushbutton/DIP input reads and IRQ flag clear, power-good reads, FMC/PCIe/SFP/reset control writes, logical GPIO-to-register mapping for boundary pins, and rejection of invalid GPIO ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-a10sr.h -->
