# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qm-rsrc.c

## Purpose
Defines the SCU resource allowlist for i.MX8QM clocks. The SCU clock core uses this sorted table to avoid registering resource IDs that are not valid on the SoC.

## Important APIs, Types, And Functions
The file contains `imx8qm_clk_scu_rsrc_table[]` and exports `const struct imx_clk_scu_rsrc_table imx_clk_scu_rsrc_imx8qm`. The data type is declared in `clk-scu.h` and consumed by `imx_clk_scu_init()` / `imx_scu_clk_is_valid()`.

## Control Flow
There is no runtime control flow in this file. At match time, the i.MX8QXP/QM clock driver passes this table as match data for `fsl,imx8qm-clk`. Later SCU clock allocation performs a binary search over this list.

## State And Persistence Behavior
State is read-only kernel data. It must stay sorted in ascending order, as the SCU core uses `bsearch()`. It has no persistence beyond the compiled kernel image.

## Dependencies And Integration Points
Depends on firmware resource constants from `dt-bindings/firmware/imx/rsrc.h` and the SCU clock table contract from `clk-scu.h`. It integrates indirectly with device-tree compatible matching and SCFW resource ownership checks.

## Risks
The main risk is table drift. Missing a valid i.MX8QM resource prevents clocks from being registered; adding an invalid resource may cause useless allocation attempts. Reordering can break binary-search validation.

## Test Signals
Boot i.MX8QM with `fsl,imx8qm-clk`, verify expected SCU clocks appear, no valid owned resources are rejected with `-EINVAL`, and invalid i.MX8QXP-only resources remain filtered.
