# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-interface.h

Purpose: internal interface contract for the CIF input/crop subdev abstraction.

Important APIs/types/functions: declares `rkcif_interface_register()`, `rkcif_interface_unregister()`, and `rkcif_interface_find_input_fmt()`. The file comment documents the design: one sink pad connected to a remote DVP companion or MIPI CSI-2 receiver, one source pad connected to one or more DMA stream abstractions.

Control flow: DVP and MIPI modules call register/unregister around their stream setup; capture start paths indirectly use `rkcif_interface_find_input_fmt()` to validate/translate active media-bus codes.

State and persistence: no state in the header; state is in `struct rkcif_interface` from `rkcif-common.h`.

Dependencies/integration: connects `rkcif-interface.c` to DVP/MIPI and platform modules.

Risks: as a small internal header, the main risk is stale declarations or comments drifting from the media topology implemented in the C file.

Test signals: compile/link plus media graph inspection showing interface subdevs correctly inserted between remote source and stream video nodes.
