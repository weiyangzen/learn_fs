<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c

## Purpose

`clk-fch.c` registers AMD FCH auxiliary output clocks for x86 platform devices, including special Stoney-family 25 MHz mux support.

## Important APIs, Types, And Functions

`fch_clk_probe()` uses platform `fch_clk_data` to access MMIO base/name, probes PCI root device ID, and registers fixed-rate `clk48MHz`, optionally fixed `clk25MHz`, an `oscout1_mux`, and an `oscout1` gate. `fch_clk_remove()` unregisters the created clocks. The supported mux CPU ID is `0x1576`.

## Control Flow

The built-in platform driver named `clk-fch` probes from AMD platform-device infrastructure. For supported ST CPU ID it creates mux plus gate and forces parent to 48 MHz. Other systems get a 48 MHz fixed parent and gate only.

## State And Persistence Behavior

Clock gate and mux state persists in FCH registers `CLKDRVSTR2` and `MISCCLKCNTL1`. Static `hws[]` stores registered clock handles across probe/remove.

## Dependencies And Integration Points

It depends on PCI root-device detection, platform data, clkdev lookup registration, and CCF fixed/mux/gate helpers.

## Risks And Test Signals

Risks include global static handles preventing multiple instances, possible off-by-count remove logic between ST and fixed cases, and direct PCI device assumptions. Test on ST and non-ST AMD systems, clkdev lookup by platform data name, mux parent selection, and gate polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-fch.c -->
