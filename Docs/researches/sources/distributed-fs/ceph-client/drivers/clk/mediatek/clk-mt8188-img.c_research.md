# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-img.c

## Purpose
`clk-mt8188-img.c` supplies MT8188 image subsystem clocks for the main IMGSYS block, three WPE islands, and DIP top/NR blocks. These gates feed image processing engines used by camera and post-processing pipelines.

## Important APIs, Types, And Functions
Important definitions are `imgsys_cg_regs`, gate arrays for `imgsys_main`, `wpe1`, `wpe2`, `wpe3`, `imgsys1_dip_top`, and `imgsys1_dip_nr`, plus matching `mtk_clk_desc` objects. `img_sys_rst_desc` provides reset-controller metadata for image subsystem reset IDs. The OF table maps six MT8188 image compatibles to those descriptors.

## Control Flow, State, And Persistence
The platform driver delegates to `mtk_clk_simple_probe()`, so descriptor data controls register mapping, gate registration, optional reset registration, and OF clock publication. The registered clocks persist as common-clock-framework providers until remove unwinds them.

## Dependencies, Integration Points, Risks, And Test Signals
The file integrates with image, WPE, and DIP device-tree nodes and common MediaTek gate operations. Risks include missing sub-block compatibles, wrong WPE/DIP gate bank offsets, and reset index drift against bindings. Test signals include successful probe of all IMGSYS nodes, WPE/DIP driver clock acquisition, reset line behavior, and image workload suspend/resume.
