<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c

## Purpose

`imx8mp-blk-ctrl.c` implements i.MX8MP HSIO and HDMI block-control PM domains. It exposes onecell providers, sequences upstream GPC domains, programs block-specific registers, exposes an HSIO PLL clock, and rejects upstream power-off while block children remain on.

## Important APIs, types, and functions

Core types are `imx8mp_blk_ctrl`, `imx8mp_blk_ctrl_domain_data`, and `imx8mp_blk_ctrl_domain`. HSIO PLL behavior is in `clk_hsio_pll_*()`. HSIO and HDMI register sequencing is in `imx8mp_hsio_blk_ctrl_power_on/off()` and `imx8mp_hdmi_blk_ctrl_power_on/off()`. `imx8mp_blk_ctrl_gpc_notifier()` guards upstream GPC transitions.

## Control flow

Probe maps registers, attaches the bus domain, creates per-domain genpds, gets clocks and ICC paths, attaches upstream GPC domains, registers per-domain GPC notifiers, registers a onecell provider and bus notifier, and optionally registers the HSIO PLL. Power-on resumes bus, enables clocks, programs block registers, resumes upstream GPC, programs ICC, and disables temporary clocks. Power-off reverses local state before releasing upstream and bus runtime PM references.

## State and persistence behavior

State persists in HSIO GPR clock/reset/PLL fields and HDMI RTX clock/reset/control fields. Software tracks upstream devices, per-domain notifiers, ICC paths, onecell pointers, and the HSIO PLL provider. USB PHY domains carry active-wakeup flags.

## Dependencies and integration points

It depends on genpd notifiers, runtime PM, common clock provider APIs, regmap, clocks, ICC, OF, and `imx8mp-power.h`. It matches HSIO and HDMI block-control compatibles.

## Risks and edge cases

Upstream pre-off rejection is essential, HSIO handshakes temporarily need USB clocks, HDMI state must be cleared on power-up because registers persist, PLL rate is fixed at 100 MHz, and notifier/runtime PM cleanup must be balanced.

## Test signals

Test HSIO/HDMI compatibles, HSIO PLL lock/timeout, USB/PCIe/HDMI domain toggles, ICC programming, upstream pre-off rejection, notifier cleanup, USB PHY wakeup behavior, suspend/resume balance, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c -->
