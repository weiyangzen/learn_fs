
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/stk1160-reg.h

## Purpose
`stk1160-reg.h` defines symbolic register addresses and bit fields for the STK1160 USB capture bridge.

## Important APIs, Types, and Functions
The header declares register groups for GPIO and wakeup (`STK1160_GCTRL`, `STK1160_RMCTL`), strap state (`STK1160_POSV_*`), decoder/capture control (`STK1160_DCTRL`, `STK1160_DMCTRL*`, `STK116_CFSPO*`, `STK116_CFEPO*`), internal serial/I2C bus (`STK1160_SICTL*`, `STK1160_SBUSW*`, `STK1160_SBUSR*`, `STK1160_ASIC`), PLL/timing (`STK1160_PLLSO`, `STK1160_PLLFD`, `STK1160_TIGEN`, `STK1160_TICTL`), AC97/I2S (`STK1160_AC97*`, `STK1160_I2SCTL`), and EEPROM size.

## Control Flow
The header has no executable flow. It enables other STK1160 source files to program reset defaults, capture windows, decimation, serial-bus transactions, AC97 commands, and streaming start/stop using named offsets and bits.

## State and Persistence
It describes hardware register state only. The actual values are volatile device state set by probe, format/std changes, streaming, I2C transactions, and AC97 setup.

## Dependencies and Integration Points
The header is included by STK1160 core, V4L2, I2C, and AC97 files. It depends on Linux `BIT()` being available through included headers.

## Risks and Edge Cases
Register aliases with overlapping addresses require byte-offset correctness when writing adjacent high/low values. Incorrect decimation bit use can corrupt UYVY chroma alignment. POSV strap bits determine whether AC97 setup is attempted; wrong bit definitions would affect audio initialization.

## Test Signals
Validate register writes with USB trace or debug register ioctls, standard-specific capture-window programming, decimation controls, I2C read/write completion bits, AC97 command bits, and start/stop writes to `STK1160_DCTRL`.
