# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_reg.h

## Purpose
`evergreen_reg.h` is a register-definition header for Evergreen/Northern Islands display, graphics-surface, cursor, LUT, HDMI, DP, UNIPHY, clock, GPIO, audio, and SMC-indirect access blocks. It provides numeric MMIO offsets and bitfield construction macros used by Radeon display and low-level ASIC code.

## Important APIs, Types, And Functions
The file exports preprocessor constants only. Major groups include SMC indirect index/data registers (`TN_SMC_IND_INDEX_0`, `TN_SMC_IND_DATA_0`), PIF/CG indirect registers, VGA memory and D3-D6 VGA controls, spread-spectrum PLL controls, audio PLL/vendor/enable registers, graphics plane registers (`EVERGREEN_GRPH_*`) with format/tiling/depth/bank macros, cursor registers (`EVERGREEN_CUR_*`), LUT registers, vline/status registers, CRTC register offsets for six display controllers, HPD GPIO registers, HDMI/DIG offsets, DP secondary stream/audio timestamp registers, and NI UNIPHY controls.

## Control Flow
There is no executable control flow. Callers compose register values through macros such as `EVERGREEN_GRPH_DEPTH(x)`, `EVERGREEN_GRPH_NUM_BANKS(x)`, `EVERGREEN_GRPH_FORMAT(x)`, `EVERGREEN_GRPH_ARRAY_MODE(x)`, `EVERGREEN_CURSOR_MODE(x)`, `NI_DIG_FE_CNTL_SOURCE_SELECT(x)`, `EVERGREEN_DP_SEC_TIMESTAMP_MODE(x)`, and `EVERGREEN_DP_SEC_N_BASE_MULTIPLE(x)`, then pass those values to Radeon register read/write helpers.

## State And Persistence Behavior
The header itself has no state. Its constants describe hardware state locations and bit layouts. Values written using these definitions persist in GPU display/audio hardware until reprogrammed or reset. The CRTC/DIG/DP offset constants encode the repeated-block layout used to address one of up to six controllers.

## Dependencies And Integration Points
`evergreen_reg.h` is consumed by Radeon display, audio, power, and ASIC setup code that needs direct Evergreen-family MMIO definitions. It complements broader generated or hand-written register headers such as `evergreend.h`; this file focuses on a subset of display/audio/graphics-plane definitions that other C files can include without embedding magic numbers.

## Risks
Register headers are fragile because a wrong offset or bit shift can silently program unrelated hardware. The macros do little validation beyond masking input width, so callers must pass valid enum values. Repeated block offsets must match actual ASIC layout; off-by-one controller offsets can affect the wrong CRTC, DIG, or DP block. Another risk is naming overlap with definitions in adjacent Radeon headers.

## Test Signals
Build tests catch duplicate or missing definitions. Functional signals include successful modeset across all CRTCs, cursor programming, LUT updates, page flips, HPD detection, HDMI/DP audio packet enablement, and UNIPHY enable/disable behavior. Register dumps comparing programmed values to expected bitfields are the most direct validation for this header.
