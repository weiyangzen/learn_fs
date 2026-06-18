# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.c

Purpose: provides static hardware configuration tables for many MDP5 revisions and selects the active configuration at KMS init.

Important APIs and functions: `mdp5_cfg_init()` chooses a config by major/minor revision, sets the global `mdp5_cfg`, and returns a handler. `mdp5_cfg_get_hw_config()`, `mdp5_cfg_get_config()`, and `mdp5_cfg_get_hw_rev()` expose selected data. Static `mdp5_cfg_hw` entries describe block counts, register bases, capabilities, SMP layout, CTL flush masks, layer mixers, pingpongs, DSPPs, CDM/DSC, interfaces, performance inefficiency factors, and max clock for chip families such as msm8x26, msm8x74, apq8084, msm8x16, msm8x36, msm8x94, msm8x96, msm8x76, msm8x53, msm8917, and msm8937.

Control flow: `mdp5_cfg_init()` allocates a handler, selects the revision table for major version 1, searches for matching minor revision, publishes the global pointer, and stores revision/config in the handler.

State and persistence: all tables are static const data; selected handler is devm-managed. The global `mdp5_cfg` is runtime global state used by generated register helpers.

Dependencies and integration: used by MDP5 KMS, CTL manager, mixer, SMP, plane, and generated `mdp5.xml.h` offset logic.

Risks: the global pointer means only one active MDP5 config is represented process-wide. Incorrect table values cause bad register offsets, resource counts, or flush masks. Unsupported revisions fail probe.

Test signals: probe each supported revision, verify config name/log, register offsets, CTL/mixer/plane counts, interface mappings, and max clock/perf behavior.
