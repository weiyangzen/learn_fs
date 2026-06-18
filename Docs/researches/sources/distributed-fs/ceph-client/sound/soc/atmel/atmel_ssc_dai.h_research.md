# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_ssc_dai.h

## Purpose
This header declares the internal Atmel SSC ASoC interface shared with machine drivers and the SSC DAI implementation.

## Important APIs, Types, And Functions
It defines SSC clock-divider IDs `ATMEL_SSC_CMR_DIV`, `ATMEL_SSC_TCMR_PERIOD`, and `ATMEL_SSC_RCMR_PERIOD`; direction masks; SSC bit-field values missing from the generic SSC header; `struct atmel_ssc_state`; `struct atmel_ssc_info`; and exported functions `atmel_ssc_set_audio(int ssc_id)` / `atmel_ssc_put_audio(int ssc_id)`.

## Control Flow
No executable control flow in the header. Machine drivers call the exported functions to allocate and release SSC audio ownership.

## State And Persistence
`struct atmel_ssc_info` describes persistent per-SSC runtime state: ownership mask, initialization state, DAI format, dividers, DMA params, saved registers, and clock rate. `struct atmel_ssc_state` is used across suspend/resume.

## Dependencies And Integration Points
It depends on `linux/atmel-ssc.h` and `atmel-pcm.h`. It is included by `atmel_ssc_dai.c` and board drivers such as `atmel_wm8904.c`.

## Risks And Test Signals
Risk is ABI drift between the header's fields and implementation assumptions, especially divider IDs and saved register fields. Test signals are successful compilation of machine drivers using the exported functions and runtime suspend/resume restoring SSC state.
