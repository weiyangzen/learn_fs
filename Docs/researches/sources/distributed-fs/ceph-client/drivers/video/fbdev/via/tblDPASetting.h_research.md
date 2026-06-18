<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h

Purpose: Header for DPA clock range thresholds and extern declarations of graphics DPA setting tables.

Important APIs/types/functions: Defines `DPA_CLK_30M`, `DPA_CLK_50M`, `DPA_CLK_70M`, `DPA_CLK_100M`, `DPA_CLK_150M`, enum `DPA_RANGE`, and externs for `GFX_DPA_SETTING_TBL_VT3324`, `GFX_DPA_SETTING_TBL_VT3327`, and `GFX_DPA_SETTING_TBL_VT3364`.

Control flow and state: No executable flow. It gives `vt1636.c` the symbolic clock-range indices used to select table rows. State is static read-only table data in the `.c` file.

Dependencies and integration points: Includes `global.h` for `struct GFX_DPA_SETTING`. Risks are array declarations not uniformly sized and tight coupling between enum order and table row order. Test signals are compile coverage and VT1636 skew patch tests across all `DPA_RANGE` branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/tblDPASetting.h -->
