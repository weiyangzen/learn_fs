<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 179-line, 4473-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `133` `#define` constants, with directly parsed numeric values spanning `0..60`. The largest macro families are `HI6220_MMC0` (12), `HI6220_MMC1` (12), `HI6220_MMC2` (12), `HI6220_PLL` (9), `HI6220_ISP` (5), `HI6220_ADE` (4). Early IDs include `HI6220_NONE_CLOCK`, `HI6220_REF32K`, `HI6220_CLK_TCXO`, `HI6220_MMC1_PAD`, `HI6220_MMC2_PAD`, `HI6220_MMC0_PAD`; the trailing IDs include `HI6220_PLL_MEDIA_GATE`, `HI6220_PLL0_BBP_GATE`, `HI6220_DDRC_SRC`, `HI6220_DDRC_AXI1`, `HI6220_POWER_NR_CLKS`, `HI6220_ACPU_SFT_AT_S`. Sentinel or count-style constants visible in this header are `HI6220_AO_NR_CLKS`, `HI6220_SYS_NR_CLKS`, `HI6220_MEDIA_NR_CLKS`, `HI6220_POWER_NR_CLKS`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `clk in Hi6220 AO (always on) controller`, `fixed rate clocks`, `fixed factor clocks`, `gate clocks`, `clk in Hi6220 systrl`, `gate clock`, `mux clocks`, `divider clocks`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi6220-clock.h -->
