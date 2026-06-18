# sources/distributed-fs/ceph-client/drivers/bus/imx-weim.c

Purpose: configures Freescale/NXP i.MX WEIM/EIM external memory bus chip-select timing and creates platform children for devices connected to the external bus. It supports several i.MX variants with different chip-select counts, register counts, strides, and burst clock controls.

Important APIs and types: `struct imx_weim_devtype` describes SoC register layout; `struct cs_timing_state` records timing already applied per chip select to reject conflicts; `weim_timing_setup()` parses `fsl,weim-cs-timing`; `imx_weim_gpr_setup()` programs i.MX50/6 GPR chip-select address layout; dynamic OF notifier creates/destroys children at runtime when enabled.

Control flow: probe maps the WEIM base, enables the clock, and calls `weim_parse_dt()`. Parsing optionally configures GPR ranges, applies burst-clock flags, walks available child nodes, writes timing registers for chip selects referenced in each child `reg`, then populates child platform devices if any timing succeeded.

State and persistence: timing state is cached per chip select to catch contradictory DT overlays. Hardware timing and WCR/GPR bits persist until reset or later writes. Dynamic notifier updates timing and child devices for added/removed nodes.

Dependencies and integration: depends on OF address/range parsing, clocks, syscon/regmap for IOMUXC GPR, OF dynamic reconfiguration, and default platform population. It is a bridge for NOR flash, SRAM, or peripherals on WEIM.

Risks: DT `ranges`, child `reg`, and timing array sizes must match the SoC layout; conflicting timing for shared chip selects fails. Dynamic node add clears fw_devlink's not-device flag before creating children. Test signals include each compatible variant, valid/invalid GPR range encodings, burst-clock options, multiple `reg` entries per child, shared CS conflict detection, OF_DYNAMIC add/remove, and child population failures.
