# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-reg.h

## Purpose
`cx88-reg.h` is the register and bitfield map for cx2388x/cx88 hardware. It gives the rest of the driver symbolic names for PCI function control, DMA engines, video/audio/TS/VIP/host blocks, GPIO/I2C, RISC instructions, interrupt masks, audio mode constants, and video format constants.

## Important APIs, Types, And Functions
This header contains no functions; its API is preprocessor constants. Major groups include PCI config aliases, DMA interrupt/status registers, DMA channel pointers/counts, video registers, audio DSP registers, TS registers, GPIO/I2C registers, RISC opcodes, and capability constants such as `PCI_INT_IR_SMPINT`, `EN_BTSC_*`, `CX23880_CAP_CTL_*`, and `ColorFormat*`.

## Control Flow
There is no executable control flow. The constants drive control flow in other files by selecting register offsets and bit masks for DMA start/stop, interrupt acknowledgement, audio-standard programming, input muxing, and I2C/IR bit-banging.

## State, Persistence, And Dependencies
The header has no mutable state. Its values are an implicit ABI between driver code and the cx2388x memory-mapped register layout. It is included by `cx88.h`, which wraps these offsets with `cx_read()`, `cx_write()`, and related helpers.

## Integration Points
Every cx88 functional module depends on this header: video/VBI use video DMA and capture bits, MPEG uses TS registers and channel 28, input uses GPIO/IR sample registers, I2C uses `MO_I2C`, audio uses `AUD_*`, and core code uses RISC opcodes and SRAM channel register addresses.

## Risks
Misdefined offsets or masks cause direct hardware misprogramming and can manifest as silent capture failure, bus errors, IRQ storms, or corrupt DMA. Comments include a FIXME about possible host register typos, so host-related definitions deserve caution. Duplicate-style aliases such as `AUD_APB_IN_RATE_ADJ`/`AUD_I2SCNTL` intentionally share an offset and must not be "cleaned up" blindly.

## Test Signals
Validation is indirect: successful capture, VBI, MPEG TS, audio, I2C, and IR operation across boards. Register-dump comparisons against known hardware docs, IRQ mask/status sanity, RISC DMA completion, and `CONFIG_VIDEO_ADV_DEBUG` register reads are useful when touching this file.
