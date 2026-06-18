# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isph3a_af.c

## Purpose
`isph3a_af.c` implements the H3A Auto Focus statistics subdevice through the generic `ispstat` framework. It validates AF paxel, IIR, HMF, RGB-position, and focus-value mode settings; stages config changes; programs AF registers and coefficient tables; toggles the AF engine; and exposes private ioctls for configuration and statistics.

## Important APIs, Types, And Functions
- `h3a_af_validate_params()` validates horizontal/vertical paxel count, paxel size and increment, start positions, IIR coefficient bounds, IIR start, the known 12-pixel corruption case, and buffer size.
- `h3a_af_setup_regs()` writes the stats buffer address, paxel geometry, IIR start, two coefficient sets, and PCR bits for RGB position, focus-value mode, A-law, and median filter.
- `h3a_af_set_params()` compares all relevant fields, copies the user config when changed or not yet configured, updates config counters, and computes exact buffer size.
- `h3a_af_ioctl()` handles AF config, stat request, time32 stat request, and enable ioctls.
- Public lifecycle: `omap3isp_h3a_af_init()` and `omap3isp_h3a_af_cleanup()`.

## Control Flow
Initialization allocates current and recovery configs, populates minimum valid paxel defaults, validates and sizes the recovery config, stores ops/event metadata, and initializes the stat subdevice. Userspace ioctls flow through generic stat helpers into validation and set callbacks. On hardware setup, the active buffer address is always refreshed when enabled, while full register programming occurs only if `af->update` is set. Enable toggles `ISPH3A_PCR_AF_EN` and the AF subclock.

## State And Persistence
AF persistent state is in `isp->isp_af` and the private `omap3isp_h3a_af_config`. The generic stat framework tracks buffer state, update flags, configuration counters, recovery config, and enabled/disabled state. Hardware AF registers are treated as derived volatile state.

## Dependencies And Integration Points
It depends on the OMAP3 ISP ABI AF config structs/limits, H3A register macros, ISP register helpers, ISP subclock helpers, V4L2 subdev ioctl/event operations, and `ispstat` for common stats behavior.

## Risks And Edge Cases
- AF coefficient programming assumes `OMAP3ISP_AF_NUM_COEF` includes index 10 and writes paired coefficients up to index 9 plus standalone index 10.
- The hardware corruption workaround rejects more than nine windows when paxel area is exactly 12; regression tests should preserve this behavior.
- `h3a_af_set_params()` jumps out at the first changed field and then copies the full struct, which is correct but makes diff-based reasoning less direct.
- Shared H3A PCR bits must be modified using masks to avoid clobbering AEWB fields.

## Test Signals
Boundary tests for paxel count/size/start/increment, IIR coefficient maximums, invalid 12-area/many-window case, known config-to-register encodings, ioctl dispatch, recovery-config validation, stat buffer sizing, and AF enable/busy behavior are the strongest signals.
