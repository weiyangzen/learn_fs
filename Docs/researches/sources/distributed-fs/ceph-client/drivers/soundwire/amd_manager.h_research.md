# sources/distributed-fs/ceph-client/drivers/soundwire/amd_manager.h

## Purpose
Defines AMD ACP SoundWire manager register offsets, bit masks, timing constants, port limits, and per-revision DAI-to-register maps used by `amd_manager.c`. It is the hardware programming contract for AMD SoundWire managers.

## Important APIs, Types, and Functions
The key type is `struct sdw_manager_dp_reg`, mapping a manager port to frame-format, sample-interval, hctrl, offset, and lane/channel-enable registers. The file defines ACP common registers (`ACP_PAD_PULLDOWN_CTRL`, `ACP_SW_PAD_KEEPER_EN`, `ACP_EXTERNAL_INTR_*`, wake registers), manager registers (`ACP_SW_EN`, `ACP_SW_FRAMESIZE`, immediate command/response, status masks, BPT/BRA registers), command/response bitfields, interrupt masks, PM and wake masks, DPN frame/offset/channel fields, and arrays `acp63_sdw0_dp_reg`, `acp63_sdw1_dp_reg`, `acp70_sdw_dp_reg`, and `sdw_manager_reg_mask_array`.

## Control Flow
The header has no runtime flow, but `amd_manager.c` selects an array based on ACP revision and manager instance. Those arrays drive every data-port register write during stream parameter setup and channel enable/disable. Interrupt setup uses `sdw_manager_reg_mask_array` to select the ACP external interrupt bit for SDW0 or SDW1.

## State and Persistence Behavior
Despite being a header, it defines `static` register-map arrays in every translation unit that includes it. In this build it is included by `amd_manager.c`, so the arrays are private copies. The constants model persistent hardware layout and must stay aligned with ACP revisions. No software state is stored here beyond compile-time data.

## Dependencies and Integration Points
Includes `linux/soundwire/sdw_amd.h` for manager counts and revision/instance definitions. It is tightly coupled to AMD ACP register documentation and the DAI numbering used by the AMD DMA and ASoC paths. The comments document required CPU DAI to manager port mapping for SDW0 and SDW1.

## Risks
Incorrect offsets, masks, or DAI array ordering can route audio to the wrong ACP data port or corrupt shared ACP state. The register-map arrays are `static` in a header, which is safe for single use but undesirable if included by multiple C files. Port counts must match the arrays; any new ACP revision needs explicit mapping. Bit masks for wake, device state, and interrupts affect suspend/resume reliability.

## Test Signals
Review ACP register writes during playback/capture on every port, compile with all AMD-supported revisions, verify SDW0 six-DAI and SDW1 two-DAI mapping, validate external interrupt masks for both instances, and test suspend/resume wake masks and device-state programming on ACP70+.
