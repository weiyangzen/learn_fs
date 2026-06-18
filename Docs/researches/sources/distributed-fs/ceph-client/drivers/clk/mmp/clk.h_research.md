# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.h

Purpose: shared private header for MMP clock drivers, defining custom clock data structures, parameter table formats, helper prototypes, and power-domain APIs.

Important APIs/types: defines `mmp_clk_factor`, `mmp_clk_mix`, `mmp_clk_gate`, `mmp_clk_unit`, parameter structs for fixed-rate/factor/gate/mux/div/PLL clocks, `mmp_clk_mix_config`, `mmp_clk_mix_reg_info`, `DEFINE_MIX_REG_INFO`, and `mmp_pm_domain_register`.

Control flow: the header itself has no runtime control flow, but its descriptor types drive the table loops in `clk.c`, custom registration in `clk-frac.c`, `clk-gate.c`, `clk-mix.c`, `clk-pll.c`, and power islands.

State and persistence: structs describe persistent CCF objects and MMIO-backed register metadata. `mmp_clk_unit` is the central provider state for onecell lookups.

Dependencies and integration: includes CCF provider APIs, math helpers, PM domains, and clkdev. It is the integration contract between generic MMP helper files and SoC-specific clock tables.

Risks: bit macros use `1 << width`, so invalid widths can overflow. Many fields are raw shifts/masks/offsets supplied by tables; no central validation prevents out-of-range IDs or register fields.

Test signals: build coverage for all MMP clock files, sparse/static analysis of table initializers, and binding/table consistency checks.
