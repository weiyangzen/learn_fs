# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-aon.c

## Purpose
This module registers the JH7110 always-on clock controller for GMAC0, OTPC, RTC, and AON APB functional clocks.

## Important APIs, Types, And Functions
`jh7110_aonclk_data[]` encodes the AON clock topology. `jh7110_aoncrg_probe()` registers each clock through the shared JH71x0 core and then calls `jh7110_reset_controller_register(priv, "rst-aon", 1)` to expose the associated reset controller.

## Control Flow
Probe maps registers, registers local clocks with parent data resolved to either local hardware or firmware names (`osc`, `gmac0_rmii_refin`, `gmac0_rgmii_rxin`, `stg_axiahb`, `apb_bus`, `gmac0_gtxclk`, `rtc_osc`), adds the OF clock provider, then registers reset auxiliary device `rst-aon`.

## State And Persistence
Hardware register state controls gates, muxes, divider values, and inversion for GMAC and RTC paths. The module retains `jh71x0_clk_priv` state and the shared read-modify-write lock.

## Dependencies And Integration Points
It depends on JH7110 SYS clocks for several firmware-named parents and on the reset helper exported by the SYS driver. It integrates with `dt-bindings/clock/starfive,jh7110-crg.h` and compatible `starfive,jh7110-aoncrg`.

## Risks
Because it is a module depending on SYS, loading before parent clocks or reset helper availability would fail. GMAC0 TX/RX inversion and RMII/RGMII parent selection are hardware-mode sensitive.

## Test Signals
GMAC0 operation in RGMII and RMII modes, RTC 32k selection, reset-controller registration, and module probe/remove tests are key signals.
