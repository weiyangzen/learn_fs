# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.c

## Purpose
This file implements MDP3 component discovery, clock/runtime-PM control, component context binding, and per-component CMDQ register programming operations. It covers RDMA, RSZ, WROT, WDMA, TDSHP, COLOR, CCORR, AAL, HDR, FG, OVL, PAD, and merge-assisted paths.

## Important APIs, Types, and Functions
The central operation tables are `rdma_ops`, `rsz_ops`, `wrot_ops`, `wdma_ops`, `tdshp_ops`, `color_ops`, `ccorr_ops`, `aal_ops`, `hdr_ops`, `fg_ops`, `ovl_ops`, and `pad_ops`, collected in `mdp_comp_ops[]`. Public APIs include `mdp_comp_config()`, `mdp_comp_destroy()`, `mdp_comp_clocks_on()`, `mdp_comp_clocks_off()`, `mdp_comp_clock_on()`, `mdp_comp_clock_off()`, and `mdp_comp_ctx_config()`. Static helpers bind DT nodes to `struct mdp_comp`, read CMDQ subsys IDs/events, map aliases to public IDs, and handle platform flags.

## Control Flow
Probe-time `mdp_comp_config()` scans sibling DT nodes, matches component compatibles, assigns alias IDs, creates components, gets clocks/MMIO/CMDQ subsys IDs/GCE events, enables runtime PM for DMA-capable blocks, and then creates subcomponents. At job time, CMDQ path setup calls `mdp_comp_ctx_config()` to bind SCP component params to actual components and frame inputs/outputs. Component ops reset/init blocks, write frame-level state, write subframe/tile state, wait EOF events for DMA blocks, optionally advance subframes, and postprocess through CMDQ macros.

## State and Persistence
Persistent device-lifetime state is in `mdp->comp[]` entries: component device, public/inner/alias IDs, type, reg base, mapped regs, clocks, subsys ID, GCE events, ops, and MDP backpointer. Global static state includes alias counters and `p_id`, set during component config. In-flight state is `struct mdp_comp_ctx`, which points at shared SCP params and frame inputs/outputs.

## Dependencies and Integration Points
The file depends on OF/platform device lookup, clocks, runtime PM, CMDQ client register lookup, MediaTek MMSYS helpers, MDP3 config data, register headers for each block, and SCP shared-memory structures. It is called by core probe/remove and CMDQ path construction.

## Risks and Edge Cases
The global `p_id` and alias counters assume one active platform configuration path at a time. `mdp_comp_destroy()` frees components with `devm_kfree(mdp->comp[i]->comp_dev, ...)` even though allocation used the parent MDP device, which deserves lifecycle review. `mdp_comp_clocks_on()` does not unwind previously enabled components if a later component or auxiliary blend clock fails. Missing EOF GCE events are fatal only for DMA-capable components. WDMA programming is MT8183-only in several reads. Full correctness depends on SCP-generated fields matching the selected SoC ABI and register masks.

## Test Signals
Probe on MT8183/MT8188/MT8195 DTs, missing clocks/events, runtime PM balance, component alias ordering, CMDQ packet inspection for every component type, 10-bit/UFO RDMA, RSZ merge paths, WROT rotations, WDMA output, HDR/AAL/TDSHP/FG/OVL/PAD paths, mailbox error unwind, and remove/unbind leak checks are the best validation signals.
