# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-imx8qxp-lpcg.c

## Purpose
Registers i.MX8QXP LPCG gate clocks for subsystem clock-gate blocks. It supports legacy subsystem tables for ADMA, connectivity, and LSIO, and a newer generic DT binding where clock indices, parents, and output names are parsed from each LPCG node.

## Important APIs, Types, And Functions
`struct imx8qxp_lpcg_data` describes one gate: DT id, name, parent, flags, register offset, bit index, and hardware autogate support. `struct imx8qxp_ss_lpcg` groups a subsystem table and maximum clock count. `imx_lpcg_parse_clks_from_dt()` implements the new `fsl,imx8qxp-lpcg` binding. `imx8qxp_lpcg_clk_probe()` tries that path first, then falls back to static subsystem tables. `imx_lpcg_of_clk_src_get()` maps `clock-indices` bit offsets to onecell entries by dividing by four.

## Control Flow
Probe first attempts DT-driven registration. That path ioremaps the node resource, reads `clock-indices`, parent names, and output names, enables runtime PM with autosuspend, registers each LPCG through `imx_clk_lpcg_scu_dev()`, adds a devm clock provider, then autosuspends. On failure it unregisters created clocks and disables runtime PM.

If DT parsing is not applicable, the legacy path obtains match data, maps the subsystem range with `devm_ioremap()` rather than `devm_platform_ioremap_resource()` to allow overlapping peripheral mappings, allocates onecell data, registers static LPCG clocks with `imx_clk_lpcg_scu()`, warns about registration errors, and publishes the provider.

## State And Persistence Behavior
Kernel state is onecell clock arrays and allocated LPCG clock objects. Hardware state is the LPCG register gate bits. Runtime/system suspend state for individual gates is handled by the shared LPCG-SCU implementation and `imx_clk_lpcg_scu_pm_ops`.

## Dependencies And Integration Points
Depends on `clk-lpcg-scu.c`, `clk-imx8qxp-lpcg.h` register offsets, `dt-bindings/clock/imx8-clock.h`, runtime PM, OF clock providers, and SCU clock parents created by `clk-imx8qxp.c`.

## Risks
The old mapping path intentionally avoids reserving the memory region; changing it can break overlapping devices such as UARTs. DT-driven indexing assumes bit offsets are multiples of four and below eight outputs. Parent/output-name count mismatches and partial registration failures must keep cleanup correct.

## Test Signals
Test legacy ADMA/CONN/LSIO nodes and new generic LPCG nodes, verify clock lookup by phandle index, runtime PM autosuspend/resume, serial/network/storage peripherals behind LPCGs, and suspend/resume restoration.
