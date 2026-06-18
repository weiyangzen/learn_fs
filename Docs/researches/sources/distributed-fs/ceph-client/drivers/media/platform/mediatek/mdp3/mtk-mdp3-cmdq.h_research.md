# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.h

## Purpose
This header defines the public command-queue submission contract for MDP3.

## Important APIs, Types, and Functions
`struct mdp_cmdq_param` packages SCP config, frame parameters, output compose rectangles, optional user callback/data, and mem2mem context. `struct mdp_cmdq_cmd` stores the in-flight CMDQ packet, callback work, event pointer, device, callback data, copied component list, context, PP index, and component count. `mdp_cmdq_send()` submits work.

## Control Flow
Higher layers fill `mdp_cmdq_param` after SCP frame configuration and call `mdp_cmdq_send()`. The implementation allocates `mdp_cmdq_cmd` instances and frees them after mailbox callback cleanup.

## State and Persistence
The parameter is caller-owned per job. `mdp_cmdq_cmd` is in-flight state owned by the CMDQ implementation until callback release.

## Dependencies and Integration Points
It includes platform device, V4L2, MediaTek CMDQ, and image IPI definitions. It forward-declares `struct mdp_dev`.

## Risks and Edge Cases
The callback/data pointers are raw and must remain valid according to the submission contract. `config`, `param`, and compose pointers must cover all outputs and PP indices.

## Test Signals
Compile coverage, callback invocation tests, and job cancellation/error-path tests validate this API.
