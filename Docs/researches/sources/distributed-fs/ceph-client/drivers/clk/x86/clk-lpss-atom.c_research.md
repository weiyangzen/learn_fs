<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c

## Purpose

`clk-lpss-atom.c` registers the fixed 100 MHz Intel Atom LPSS free-running clock.

## Important APIs, Types, And Functions

`lpss_atom_clk_probe()` allocates `lpss_clk_data`, registers a fixed-rate clock named `lpss_clk`, stores the handle, and attaches driver data. `lpss_atom_clk_init()` registers the platform driver.

## Control Flow

Platform driver `clk-lpss-atom` probes during Intel LPSS initialization. There is no remove callback in this file.

## State And Persistence Behavior

The clock is modeled as fixed and has no hardware state in this driver. Runtime state is devm data plus the registered fixed-rate clock.

## Dependencies And Integration Points

It depends on Intel LPSS platform data types and CCF fixed-rate registration. LPSS device drivers consume the clock through platform integration.

## Risks And Test Signals

Risks are duplicate fixed-rate registration if multiple devices probe and no unregister path. Test LPSS devices on BayTrail/CherryTrail-style systems and verify `lpss_clk` rate is 100 MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-atom.c -->
