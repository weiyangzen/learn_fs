# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.h

Purpose: declares the MDP5 hardware configuration data model and selection API.

Important APIs and types: `struct mdp5_cfg_hw` aggregates MDP caps, SMP layout, CTL layout, VIG/RGB/DMA/cursor pipe blocks, LM instances, DSPP/AD/PP/DSC/CDM/WB blocks, interface connections, performance factors, and max clock. Supporting types define common sub-blocks, LM instances, pipe caps, CTL flush masks, SMP reserved state, writeback instances, and interface base/connect arrays. `mdp5_cfg_init()` and getter functions expose selected config. The `mdp5_cfg_intf_is_virtual()` macro classifies virtual interfaces such as writeback.

Control flow and integration: MDP5 init calls `mdp5_cfg_init()` after reading hardware version. Other modules query the handler to size pools, assign resources, compute flush masks, and program interfaces.

State and persistence: header declares extern global `mdp5_cfg`, but no storage. Config data is static and runtime-selected.

Dependencies: includes MSM driver types and generated enum/cap definitions available through display headers.

Risks: fixed maximums (`MAX_CTL`, `MAX_BASES`, `MAX_SMP_BLOCKS`, `MAX_CLIENTS`) must cover all tables. The virtual interface macro evaluates its argument once but depends on enum ordering.

Test signals: compile coverage for table initializers, probe coverage for each revision, resource manager bounds checks, and tests that generated register access uses selected bases.
