## sources/distributed-fs/ceph-client/drivers/comedi/drivers/jr3_pci.h

### Purpose
`jr3_pci.h` defines the MMIO layout and helper accessors for the JR3 DSP/sensor memory consumed by `jr3_pci.c`. It models a 16-bit DSP memory space where each word is aligned on a 32-bit PCI boundary.

### Important APIs, Types, And Functions
Inline accessors `get_u16()`, `set_u16()`, `get_s16()`, and `set_s16()` wrap `readl()`/`writel()` with 16-bit casts. Key layout types are `struct raw_channel`, `struct force_array`, `struct six_axis_array`, `struct thresh_struct`, `struct le_struct`, `struct intern_transform`, `struct jr3_sensor`, and `struct jr3_block`. Enumerations describe vector bits, warning bits, `enum error_bits_t`, and transform link types.

### Control Flow
The header has no runtime control flow, but its layout drives every MMIO read/write in `jr3_pci.c`. The driver indexes `struct jr3_block` per subdevice, writes firmware into `program_lo`/`program_hi`, resets through `reset`, and reads or commands the embedded `struct jr3_sensor`.

### State, Persistence, And Dependencies
The structures represent persistent board/DSP memory: raw sensor channels, calibration and full-scale data, offsets, filtered force arrays, rate/peak data, command words, counters, warnings/errors, load envelopes, and transforms. It depends on Linux I/O accessors and exact hardware offsets documented in comments.

### Integration Points
`jr3_pci.c` includes this header to issue DSP commands, parse sensor status, expose Comedi channels, and enforce `BUILD_BUG_ON(sizeof(struct jr3_block) != 0x80000)`.

### Risks
Any field size or padding change breaks hardware ABI. Comments are extensive but no explicit compile-time assertions cover the inner `struct jr3_sensor` offsets. The accessors discard high 16 bits, matching hardware assumptions but hiding unexpected nonzero upper data. The header is not protected by an include guard.

### Test Signals
Build should verify `struct jr3_block` size. Hardware tests should confirm firmware writes land in low/high program memory, command-word completion works, filter/full-scale/error offsets match expected values, and model/serial/copyright reads are sane.
