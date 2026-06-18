<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h` is a Linux device-tree clock binding header for the HiSilicon clock provider namespace. It assigns stable integer IDs that device-tree nodes pass through `clocks = <&provider ID>` specifiers and that the matching common-clock-framework driver uses to index its clock registration tables. The file was read as a complete 215-line, 6747-byte header; it is declarative ABI data rather than executable code.

## Important APIs, Types, and Functions

The public API is the set of `190` `#define` constants, with directly parsed numeric values spanning `0..156`. The largest macro families are `HI3660_CLK` (132), `HI3660_PCLK` (38), `HI3660_ACLK` (5), `HI3660_GATE` (3), `HI3660_AUTODIV` (2), `HI3660_CLKIN` (2). Early IDs include `HI3660_CLKIN_SYS`, `HI3660_CLKIN_REF`, `HI3660_CLK_FLL_SRC`, `HI3660_CLK_PPLL0`, `HI3660_CLK_PPLL1`, `HI3660_CLK_PPLL2`; the trailing IDs include `HI3660_CLK_IOMCU_PERI0`, `HI3660_CLK_STUB_CLUSTER0`, `HI3660_CLK_STUB_CLUSTER1`, `HI3660_CLK_STUB_GPU`, `HI3660_CLK_STUB_DDR`, `HI3660_CLK_STUB_NUM`. Sentinel or count-style constants visible in this header are `HI3660_CLK_STUB_NUM`. It defines no C structs, enums, functions, or inline helpers; consumers include the header and use the macros as numeric clock specifier cells.

## Control Flow

There is no runtime control flow in this header. Its compile-time flow is the include guard, followed by ordered macro definitions that must remain synchronized with the platform clock driver and binding documentation. Source comments group the IDs around `fixed rate clocks`, `clk in crgctrl`, `clk in pmuctrl`, `clk in pctrl`, `clk in sctrl`, `clk in iomcu`, `clk in stub clock`, `__DTS_HI3660_CLOCK_H`. The ordering often reflects hardware clock topology: fixed oscillators and PLLs first, then muxes/dividers/gates or per-subsystem clock domains, followed by sentinel count macros where present.

## State and Persistence Behavior

The header stores no mutable kernel state and performs no persistence itself. Its numeric assignments are persistent ABI because compiled device trees, board DTS files, overlays, and drivers all depend on the exact integer associated with each macro. Holes or repeated local numbering are intentional when the provider has multiple register blocks or when IDs mirror hardware tables. Commented-out definitions observed here are none; those slots should be treated cautiously because reusing them can change the meaning of older DTS sources.

## Dependencies and Integration Points

Direct preprocessor includes are none. The main integration points are platform DTS files under `arch/*/boot/dts`, YAML binding schemas for the compatible clock controller, and clock drivers under `drivers/clk/` that expose matching `clk_hw_onecell_data`, gate arrays, mux tables, reset/PLL descriptions, or PMIC clock outputs. In this repository copy under `sources/distributed-fs/ceph-client`, the file is carried as part of the kernel source imported beside Ceph client code, but its functional consumers are kernel clock and devicetree subsystems rather than distributed-filesystem logic.

## Risks and Edge Cases

The primary risk is ABI drift: renumbering, deleting, or repurposing a macro silently points existing device trees at the wrong clock. Other risks are duplicate IDs within one provider domain, off-by-one sentinel values that make drivers allocate too few entries, missing IDs for clocks referenced by DTS, and provider/domain confusion when a SoC has several clock controllers. Headers with many related families, such as mux/divider/gate groups, also risk table-order skew between the binding header and the driver arrays.

## Test Signals

Useful validation signals are `make dt_binding_check`, `make dtbs_check`, full kernel build coverage for the relevant `drivers/clk` provider, and `rg` cross-checks that every DTS use has a provider driver entry. Runtime signals are board boot logs without missing-clock probe deferrals, successful probe of dependent UART/MMC/USB/display/network/audio devices, and debugfs clock summaries showing the expected parentage and enable counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/hi3660-clock.h -->
