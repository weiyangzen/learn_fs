# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.c

## Purpose
This is the legacy MediaTek MDP platform driver core. It discovers component blocks, registers the V4L2 mem2mem video device, obtains the VPU platform device, registers a VPU watchdog reset handler, and implements global runtime/system PM clock handling.

## Important APIs, Types, and Functions
Key functions are `mtk_mdp_probe()`, `mtk_mdp_remove()`, `mtk_mdp_register_component()`, `mtk_mdp_unregister_component()`, PM callbacks, and VPU watchdog work/reset handlers. It exports the debug-level module parameter `mtk_mdp_dbg_level`.

## Control Flow
Probe allocates `struct mtk_mdp_dev`, handles old child-node and newer sibling-node DT layouts, creates and registers component records, creates job and watchdog workqueues, registers the V4L2 device and mem2mem node, obtains the VPU device, registers VPU watchdog handling, sets vb2 DMA max segment size, and enables runtime PM. Remove reverses those resources. Runtime/system suspend disables all component clocks; resume enables them. A VPU watchdog callback queues work that marks every active context error.

## State and Persistence
Driver state persists in `struct mtk_mdp_dev`: locks, component list, context list, V4L2/m2m objects, workqueues, VPU device, counters, and watchdog work. Context error flags survive until each context is released or reset by higher layers.

## Dependencies and Integration Points
The core depends on platform/OF, common clocks through components, runtime PM, V4L2/vb2, the MediaTek VPU driver, and `mtk_mdp_m2m.c` registration. It binds `mediatek,mt8173-mdp` and component compatibles under the same parent.

## Risks and Edge Cases
Old/new DT layout support requires careful parent selection. Disabled components are skipped, which may leave the VPU firmware with missing hardware paths. Probe error unwinding must keep component OF references and workqueues balanced. VPU watchdog sets all contexts into error state but does not itself drain queued buffers. Runtime PM clock-on logs but does not fail resume on individual component clock errors.

## Test Signals
Probe/remove on both DT layouts, disabled component nodes, VPU firmware absence, VPU watchdog reset, runtime suspend/resume while streaming idle, and V4L2 device registration/unregistration are high-value tests.
