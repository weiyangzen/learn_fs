# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_ops.c

## Purpose
This file provides the exported global WED operations hook used by MediaTek SoC networking code. It defines `mtk_soc_wed_ops` as an RCU-protected pointer to `struct mtk_wed_ops` and exports it to GPL modules.

## Important APIs and Types
- `const struct mtk_wed_ops __rcu *mtk_soc_wed_ops` is the shared operations table pointer.
- `EXPORT_SYMBOL_GPL(mtk_soc_wed_ops)` makes the hook available to other kernel objects.

## Control Flow
There is no executable control flow in this file. Producers and consumers elsewhere are expected to publish and dereference the pointer with RCU discipline.

## State and Persistence
The only state is the global pointer. Its value persists for the lifetime of the loaded module/kernel image and acts as a cross-driver registration point.

## Dependencies and Integration Points
It includes the public MediaTek WED SoC header, which defines `struct mtk_wed_ops`. It integrates with WED provider and consumer drivers through symbol linkage rather than direct calls.

## Risks and Test Signals
The main risk is misuse outside RCU read-side protection or publishing without the expected synchronization. Test signals are sparse: build/link coverage, module load/unload paths, and runtime WED attach/detach paths that exercise the external symbol are the practical validation points.
