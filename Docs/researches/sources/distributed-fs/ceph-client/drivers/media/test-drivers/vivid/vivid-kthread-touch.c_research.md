# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-kthread-touch.c

Purpose: implements the touch capture kernel thread for the Vivid touch input device. It schedules touch buffers at `timeperframe_tch_cap`, fills synthetic touch pressure maps, completes request controls, stamps timestamps, and handles stream lifecycle.

Important APIs and functions: exported APIs are `vivid_start_generating_touch_cap` and `vivid_stop_generating_touch_cap`. Internal functions are `vivid_thread_tch_cap_tick` and `vivid_thread_touch_cap`.

Control flow: start creates `kthread_touch_cap` unless one already exists, initializes the sequence start offset from `seq_wrap`, and marks touch streaming active. The kthread computes elapsed buffers from `jiffies`, handles resync, updates `touch_cap_with_seq_wrap_count`, calls the tick to dequeue one active touch buffer and fill it with `vivid_fillbuff_tch`, then sleeps until the next scheduled frame. Stop clears streaming, completes all queued touch buffers with error, stops the kthread, and clears the pointer.

State and persistence: volatile state lives in `struct vivid_dev`: touch active list, kthread pointer, stream flag, sequence counters and offsets, `jiffies_touch_cap`, timestamp wrap offset, and request-control state. No generated touch pattern persists beyond queued buffers except the random seed cached in `dev->tch_pat_random`.

Dependencies and integration points: depends on Linux freezer/jiffies, Vivid core, touch kthread header, and touch capture buffer generator. It integrates with videobuf2 through the active list and `vb2_buffer_done`, and with V4L2 requests through `ctrl_hdl_touch_cap`.

Risks: the resync path assigns `dev->cap_seq_resync = false` instead of `dev->touch_cap_seq_resync = false`, and the long-jiffies resync path writes `dev->cap_seq_offset` instead of `dev->touch_cap_seq_offset`; those look like copy/paste bugs that can leave touch resync state inconsistent. `dropped_bufs` is computed but unused by the tick. Timestamp assignment happens after buffer completion.

Test signals: touch capture stream cadence, sequence wrap behavior, changing timeperframe while streaming, streamoff cleanup, request API completion, timestamp wrap, and static analysis for the suspicious resync fields are useful signals.
