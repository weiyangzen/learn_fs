# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.c

## Purpose
This file converts SCP-generated MDP3 frame/config data into command queue packets. It builds component paths, programs MMSYS muxing, configures frame/subframe component registers through operation tables, prepares mutexes, sends packets via mailbox CMDQ clients, and releases clocks/mutexes on callbacks.

## Important APIs, Types, and Functions
`struct mdp_path` is the transient path builder. `mdp_cmdq_send()` is the exported entry. Internal helpers select postprocessor count, pipe/mutex, config offsets, path contexts, subframe requirements/runs, full path configuration, command preparation, and callback cleanup. `mdp_handle_cmdq_callback()` queues `mdp_auto_release_work()` for clock/mutex release and user callback/job finish.

## Control Flow
`mdp_cmdq_send()` sets a job refcount, rejects suspended devices, prepares one or two CMDQ commands depending on stream type, turns on component clocks, syncs command buffers for DMA, and sends mailbox messages. Preparation bounds-checks per-PP config, creates a packet, builds component contexts from shared config, prepares the selected mutex, runs frame setup, loops over subframes to program muxes/components/mutex/EOF waits/advance hooks, appends EOC and jump, copies component descriptors for cleanup, and installs the mailbox callback. Callback work unprepares the mutex, disables clocks, decrements job count, finishes mem2mem/user callbacks when the last PP completes, destroys packets, and frees allocations.

## State and Persistence
Runtime state is transient in `mdp_cmdq_cmd`, `mdp_path`, copied component arrays, command packets, and `mdp->job_count`. Hardware state persists only in the submitted CMDQ sequence until callback cleanup. No durable state is stored.

## Dependencies and Integration Points
The file depends on CMDQ mailbox APIs, MediaTek mutex/MMSYS helpers, MDP3 component ops, config data, MDP3 core state, V4L2 compose rectangles, and SCP shared config layouts from `mtk-img-ipi.h`.

## Risks and Edge Cases
`is_output_disabled()` currently reads `frame.output_disable` for both output and tile-disable decisions, which may be intentional ABI aliasing or a bug. `mdp_cmdq_prepare()` obtains `num_comp` from `param->config` rather than the PP-specific `config` pointer, which is subtle for dual-PP layouts. Error paths after some clocks are enabled may not destroy all prepared packets because `err_clock_off` only walks down from the failing index. Callback cleanup relies on `cmd->comps[0]` being valid and non-dummy. Refcount/job finish behavior must be correct for dual-bitblt jobs.

## Test Signals
Single- and dual-PP jobs, suspended-device cancellation, invalid config offset, dummy components, disabled output subframes, CMDQ packet decode, mailbox send failure, callback ordering, clock/mutex balance, and mem2mem job completion are critical tests.
