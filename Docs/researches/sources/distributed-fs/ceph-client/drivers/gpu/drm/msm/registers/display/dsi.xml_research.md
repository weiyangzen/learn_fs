# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi.xml

## Purpose
This XML describes the MSM DSI controller register block. It defines video-mode and command-mode programming, MIPI packet formats, triggers, active/total timing registers, DMA command transfer registers, lane status/control, interrupt bits, clocks, test-pattern generation, C-PHY mode, and DSC compression control registers.

## Important APIs, Types, and Functions
Generated APIs include `REG_DSI_*` address macros, bitfield packers for `DSI_CTRL`, `DSI_VID_CFG0`, `DSI_VID_CFG1`, `DSI_CMD_DMA_CTRL`, `DSI_CMD_CFG*`, `DSI_TRIG_CTRL`, lane status/control registers, `DSI_INTR_CTRL`, `DSI_CLK_CTRL`, `DSI_CLK_STATUS`, TPG registers, and compression mode registers. Important enums and bitsets are `dsi_traffic_mode`, `dsi_vid_dst_format`, `dsi_rgb_swap`, `dsi_cmd_trigger`, `dsi_cmd_dst_format`, `dsi_lane_swap`, TPG pattern enums, and `DSI_IRQ`.

## Control Flow
The DSI driver programs this block by enabling clocks and PHY reset, selecting lanes and video or command mode in `CTRL`, writing display timing registers, configuring command DMA or MDP stream packet payloads, selecting trigger sources, enabling error checking, and finally enabling the controller path. Interrupt flow is represented by `DSI_IRQ` status/mask fields for command DMA, command MDP, video done, BTA done, and error handling. Readback and BTA flows use `RDBK`, `RDBK_DATA_CTRL`, lane busy/status, and timeout registers.

## State and Persistence Behavior
Persistent runtime state lives in hardware registers: enabled lanes, current mode, pixel format, video timing, command stream packet words, trigger state, clock gating state, lane stop/ULPS status, TPG configuration, and DSC packetization parameters. The XML contributes no runtime storage, but generated field definitions determine how driver state is encoded across modesets, panel prepare/enable, command transfers, error recovery, and suspend/resume reprogramming.

## Dependencies and Integration Points
It is consumed by MSM DSI host, panel bridge, PHY, and KMS display code through generated register macros. It integrates with MIPI DSI packet construction, DRM display modes, MDSS/MDP output, DSI PHY timing code, runtime PM clock handling, IRQ handlers, panel command sequences, DSC configuration, and debug/test-pattern paths.

## Risks
Bitfield mistakes can corrupt timing or packet format programming and result in blank panels, underruns, failed command transfers, or DSI bus contention. The file contains overlapping offsets such as hardware version versus control naming at offset zero, version-dependent field-width comments, and late additions for C-PHY/DSC; consumers must select the right semantic view for the hardware generation. IRQ mask/status polarity must be handled carefully to avoid lost completions or interrupt storms.

## Test Signals
Signals include generated-header compilation, panel bring-up in video and command mode, command DMA completion tests, BTA/readback tests, IRQ ack/mask behavior, lane stop-state and ULPS transitions, TPG output, DSC-enabled modes, suspend/resume display restore, and underrun/error interrupt logging under stress.
