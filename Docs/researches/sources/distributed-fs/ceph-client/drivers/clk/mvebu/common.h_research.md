# sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.h

Purpose: shared MVEBU clock descriptor and helper declarations.

Important APIs/types: declares `ctrl_gating_lock`, `struct coreclk_ratio`, `struct coreclk_soc_desc`, `struct clk_gating_soc_desc`, `mvebu_coreclk_setup`, `mvebu_clk_gating_setup`, and `kirkwood_fix_sscg_deviation`.

Control flow: no runtime logic in the header; SoC files populate descriptors and pass them to common setup functions.

State and persistence: descriptors point to SoC-specific SAR decoding callbacks and static ratio/gate tables.

Dependencies and integration: included by all legacy MVEBU SoC clock files, core divider code, and common implementation.

Risks: callback contracts are informal; returning zero for unsupported SAR values is not centrally rejected. Gate descriptor arrays must be NULL-name terminated.

Test signals: compile coverage across all MVEBU SoC files and descriptor-array static checks.
