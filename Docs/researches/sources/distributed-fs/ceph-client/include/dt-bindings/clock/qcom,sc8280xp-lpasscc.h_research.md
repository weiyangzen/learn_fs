# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h` defines the public device-tree numeric IDs for the Qualcomm LPASS/audio clock-controller binding associated with `qcom,sc8280xp-lpasscc.h` / `sc8280xp`. The source was read completely for this report (17 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_LPASSCC_SC8280XP_H`. This header defines 4 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 4 numeric binding macros total.

Clock ID range: `LPASS_AUDIO_SWR_RX_CGCR`=0 through `LPASS_AUDIO_SWR_WSA2_CGCR`=2. Representative clocks: `LPASS_AUDIO_SWR_RX_CGCR`, `LPASS_AUDIO_SWR_WSA_CGCR`, `LPASS_AUDIO_SWR_WSA2_CGCR`, `LPASS_AUDIO_SWR_TX_CGCR`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LPASS_AUDIO_SWR_RX_CGCR` = 0 (clock, line 10)
- `LPASS_AUDIO_SWR_WSA_CGCR` = 1 (clock, line 11)
- `LPASS_AUDIO_SWR_WSA2_CGCR` = 2 (clock, line 12)
- `LPASS_AUDIO_SWR_TX_CGCR` = 0 (clock, line 15)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sc8280xp-lpasscc.h` IDs must stay aligned with driver tables for audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sc8280xp-lpasscc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
