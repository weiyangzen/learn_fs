# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdns3-starfive.c

Purpose: Provides the StarFive JH7110 glue layer for Cadence USB, configuring syscon strap bits, clocks, resets, child platform devices, wakeup capability, and PM clock/reset handling.

Important APIs, types, and functions: `struct cdns_starfive` stores device, syscon regmap, reset array, clocks, and syscon offset. `cdns_mode_init` sets PLL/refclk/suspend bypass bits and straps host or peripheral mode from `usb_get_dr_mode`. `cdns_clk_rst_init/deinit` enable clocks and deassert/assert resets. Probe/remove create and destroy child platform devices and PM state. Runtime and system PM callbacks toggle clocks/resets.

Control flow: Probe reads `starfive,stg-syscon` phandle argument as the USB mode register offset, gets all clocks and reset controls, writes mode strap bits, enables clocks/resets, populates children, marks wake capable, and enables runtime PM. Remove gets runtime PM, unregisters children, disables PM, and asserts resets/clocks off.

State and persistence behavior: State is in `struct cdns_starfive`, PM clock/reset state, and syscon strap register bits. No disk persistence.

Dependencies and integration points: Uses syscon/regmap, reset controller, bulk clock APIs, OF platform population, `usb_get_dr_mode`, runtime/system PM, and Cadence child nodes. Compatible string is `starfive,jh7110-usb`.

Risks: Mode strap programming only handles explicit host/peripheral and leaves other modes unchanged. `devm_clk_bulk_get_all` can return zero clocks; behavior depends on platform data. System resume calls full reset init, so child/core state must tolerate wrapper reset ordering.

Test signals: Host and peripheral DT modes, syscon phandle parsing, all clock/reset probe failures, runtime suspend/resume, system suspend/resume, child population failure, and remove while runtime suspended.
