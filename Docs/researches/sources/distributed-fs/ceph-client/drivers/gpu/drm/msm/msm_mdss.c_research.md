# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mdss.c

## Purpose
Implements the top-level Qualcomm MDSS platform driver. It manages MDSS register mapping, clocks, interconnect bandwidth, reset, chained IRQ domain, UBWC decoder programming, runtime/system PM, child device population, and platform registration for MDP5/DPU display stacks.

## Important APIs, Types, and Functions
- `struct msm_mdss` stores device, MMIO, clocks, MDP5 flag, IRQ domain/enabled mask, UBWC config data, interconnect paths, and register bus bandwidth.
- `msm_mdss_init()` performs reset, allocation, UBWC/device match data lookup, MMIO map, ICC/clock parsing, IRQ domain setup, chained IRQ install, and runtime PM enable.
- `msm_mdss_enable()` votes minimum interconnect bandwidth, enables clocks, and programs UBWC static registers for supported decoder versions.
- `msm_mdss_disable()` disables clocks and drops ICC votes.
- `msm_mdss_irq()` dispatches top-level MDSS interrupt bits into a child IRQ domain.
- `msm_mdss_setup_ubwc_dec_*()` encode per-version UBWC programming.
- `mdss_probe()` initializes MDSS and populates child platform devices; `mdss_remove()` depopulates and destroys.
- `msm_mdss_register()` and `msm_mdss_unregister()` register/unregister the platform driver.

## Control Flow
Probe determines MDP5 compatibility, calls `msm_mdss_init()`, stores drvdata, then populates child nodes. Runtime resume calls `msm_mdss_enable()`, which sets ICC bandwidth, enables clocks, and programs UBWC registers when applicable. Runtime suspend calls `msm_mdss_disable()`. The chained IRQ handler reads `REG_MDSS_HW_INTR_STATUS`, dispatches each set bit to `generic_handle_domain_irq()`, and exits the parent chip. Remove depopulates children and destroys PM/IRQ-domain state.

## State and Persistence
Runtime state is in `struct msm_mdss`, including enabled IRQ mask and ICC/clock handles. Hardware state includes UBWC static/control registers and interconnect bandwidth votes. Match-table `reg_bus_bw` constants are static. No disk persistence.

## Dependencies and Integration Points
Depends on platform/device-tree probing, irqdomain/chained IRQ APIs, runtime PM, reset controller, interconnect, clocks, Qualcomm UBWC config, generated MDSS register headers, and child display drivers populated under MDSS. KMS backends rely on MDSS clocks/ICC/IRQ hierarchy being available.

## Risks
Risks include incorrect UBWC programming for new SoCs, missing or wrong `reg_bus_bw` match data, child IRQ masking races, ICC path absence, reset timing assumptions, and top-level clock dependencies that vary between MDP5 and DPU. The x1e80100 match includes a TODO placeholder for real bandwidth.

## Test Signals
Probe on each compatible SoC, runtime PM suspend/resume, child device population, child IRQ delivery, UBWC register values for compressed framebuffer formats, interconnect votes during enable/disable, and clean remove with IRQ domain and chained handler removed.
