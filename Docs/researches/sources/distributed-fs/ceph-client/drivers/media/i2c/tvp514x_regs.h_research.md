# sources/distributed-fs/ceph-client/drivers/media/i2c/tvp514x_regs.h

Purpose: Defines the TVP5146/TVP5147 register offsets, status bits, video-standard encodings, register-script tokens, and `struct tvp514x_reg` used by the TVP514x decoder driver.

Important APIs, types, and functions: The header exports macros for analog front-end, video standard, luma/chroma controls, timing windows, formatter controls, status, chip ID, VDP, VBUS, FIFO, and interrupt registers. It defines expected chip IDs `TVP514X_CHIP_ID_MSB`, `TVP5146_CHIP_ID_LSB`, and `TVP5147_CHIP_ID_LSB`; video-standard bits for auto, NTSC, PAL variants, SECAM, and PAL60; status lock bits used by standard query; token constants `TOK_WRITE`, `TOK_TERM`, `TOK_DELAY`, and `TOK_SKIP`; and `struct tvp514x_reg { u8 token; u8 reg; u32 val; }`.

Control flow: None directly. `tvp514x.c` iterates arrays of `struct tvp514x_reg`, using token values to write, skip, delay, or terminate scripts.

State and persistence: None. The definitions describe hardware register state but do not store state themselves.

Dependencies and integration points: Included by `tvp514x.c`. The token structure is shared by the default configuration table and variant init sequences. Status and standard macros are used by the driver's autodetection and lock checking paths.

Risks: The header is broad and primarily offset-based, with few masks beyond standard/status fields, so call sites must manually encode register values. Some comments preserve spelling mistakes from older code, which is harmless but can confuse searches. The token ABI is local to this driver; if new token values are added, `tvp514x_write_regs()` must be extended in lockstep.

Test signals: Build coverage validates macro availability. Functional validation should execute token scripts containing write, skip, delay, and term entries, verify chip ID comparisons, and test status lock-bit combinations for CVBS and S-Video standard detection.
