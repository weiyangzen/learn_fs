
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-util.c

## Purpose
This file implements byte-wide indirect register access for TW5864 sub-blocks. The indirect bus is used for video decoder, audio, reset, clock, crop, and motion-detection registers that are not exposed as ordinary direct MMIO offsets.

## Important APIs, Types, And Functions
The public APIs are `tw5864_indir_writeb(struct tw5864_dev *dev, u16 addr, u8 data)` and `tw5864_indir_readb(struct tw5864_dev *dev, u16 addr)`. Callers normally use the `tw_indir_writeb` and `tw_indir_readb` convenience macros from `tw5864.h`.

## Control Flow
Both functions poll `TW5864_IND_CTL` bit 31 until the indirect controller is idle or a retry counter expires. Writes then store the byte in `TW5864_IND_DATA` and issue an indirect write command with address, `TW5864_RW`, and `TW5864_ENABLE`. Reads issue an indirect read command, poll again for completion, and return `TW5864_IND_DATA`.

## State And Persistence
The functions mutate hardware indirect registers and report only timeout errors via `dev_err`. They do not maintain software state or return explicit error codes.

## Dependencies And Integration Points
The implementation depends on `tw5864.h` for `struct tw5864_dev`, direct MMIO helpers, and register constants from `tw5864-reg.h`. It is used by video initialization, controls, standard detection, debug register access, reset, and clock setup.

## Risks
Timeouts are logged but not propagated, so callers may proceed after failed indirect transactions. The polling loop is a tight busy loop with a fixed retry count and no delay. Read returns the full `readl` value truncated to `u8`, which is intended but assumes the data byte is in the low bits.

## Test Signals
Hardware tests should watch for "retries exhausted" logs during probe, control changes, standard detection, and streaming. Successful setting of brightness/contrast/hue/saturation and input standard probing is a practical validation of indirect read/write behavior.
