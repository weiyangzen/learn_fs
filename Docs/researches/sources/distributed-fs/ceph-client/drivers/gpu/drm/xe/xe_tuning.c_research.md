# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tuning.c

Purpose: Defines platform/engine/LRC tuning tables and processes them through the Xe RTP rules engine into saved-register state for GT, hardware engine, and logical-ring-context programming.

Important APIs/types/functions: Static tables `gt_tunings`, `engine_tunings`, and `lrc_tunings` contain `xe_rtp_entry_sr` entries with names, match rules, and register actions. Public functions are `xe_tuning_init`, `xe_tuning_process_gt`, `xe_tuning_process_engine`, `xe_tuning_process_lrc`, and `xe_tuning_dump`. KUnit visibility exports are provided for GT and engine processing.

Control flow: Init allocates one DRM-managed bitmap block for active tuning tracking and partitions it among GT, engine, and LRC arrays. Processing functions create an RTP context for the target object, enable active tracking against the matching bitmap, and call `xe_rtp_process_to_sr` to append register actions to `gt->reg_sr`, `hwe->reg_sr`, or `hwe->reg_lrc`. LRC processing marks actions as context-image actions. Dump walks active bitmaps and prints applied tuning names.

State and persistence behavior: Persistent state is the active tuning bitmaps stored under `gt->tuning_active.*` and saved-register lists in GT/HWE objects. The table data is static const. DRM-managed allocation ties lifetime to the Xe device.

Dependencies and integration points: Depends on RTP rule/action macros, platform version checks, engine class matching, SR-IOV header availability, register definitions, and DRM printer/debug support. Integrated with GT/engine initialization and debugfs or diagnostics that dump active tunings.

Risks: Tuning tables encode hardware-specific register workarounds/performance settings; wrong platform ranges, media/graphics version rules, or engine-class filters can program invalid registers or omit required tuning. Bitmap allocation must match table sizes. LRC tunings must only target registers present in context images.

Test signals: KUnit tests can call exported processing functions against synthetic platform/engine contexts. Hardware bring-up should compare active dump output to expected tuning sets per platform/engine, and register state tests should validate saved-register programming.
