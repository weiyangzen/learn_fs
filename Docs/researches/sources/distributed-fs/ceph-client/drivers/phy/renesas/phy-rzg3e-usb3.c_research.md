# sources/distributed-fs/ceph-client/drivers/phy/renesas/phy-rzg3e-usb3.c

## Purpose
This driver initializes the Renesas RZ/G3E USB3 PHY test/control register block. It performs both USB2 test PHY setup and USB3 test PHY setup, provides a single generic PHY, and handles noirq system sleep reset sequencing.

## Important APIs, Types, And Functions
`struct rz_usb3` tracks the MMIO base, shared reset control, and `skip_reinit` flag used after resume. `rzg3e_phy_usb2test_phy_init()` programs UTMI control, pre-emphasis, OTG tune, SIDDQ release, and port resets. `rzg3e_phy_usb3test_phy_init()` drives CREG/RST/CLK/LANE registers, waits for SRAM init with `readl_poll_timeout_atomic()`, and releases override state. `rzg3e_phy_usb3_init_helper()` composes both halves. `rzg3e_phy_usb3_init()` is the generic PHY callback.

## Control Flow
Probe maps MMIO, obtains a shared reset already deasserted, enables runtime PM through `devm_pm_runtime_enable()`, creates the PHY, attaches driver data, and registers a simple provider. A normal PHY init runs the helper unless `skip_reinit` is true. System suspend drops runtime PM usage, asserts reset, and clears `skip_reinit`. Resume deasserts reset, resumes runtime PM, executes the full init helper immediately, then sets `skip_reinit` so the next PHY `.init` does not duplicate the hardware sequence.

## State And Persistence
The only persistent software state is `skip_reinit`, which bridges system resume and the generic PHY user's later init call. Register programming is volatile hardware state. Reset assertion on suspend clears the PHY, and resume deliberately restores it before normal users run.

## Dependencies And Integration Points
The driver uses generic PHY, platform MMIO resources, reset controller APIs, runtime PM, delay and polling helpers, and compatible string `renesas,r9a09g047-usb3-phy`. It is consumed by USB controller nodes through a simple OF PHY phandle.

## Risks And Test Signals
Initialization is timing and poll sensitive; a failure to observe `USB3_TEST_RAMCTRL_SRAM_INIT_DONE` fails PHY init/resume. Resume uses runtime PM and reset in noirq sleep callbacks, so ordering against USB controller resume is important. Test signals include successful SRAM poll, correct reset deassert/assert sequence, no duplicate reinit after resume, failure unwinding that reasserts reset and drops PM, and USB2/USB3 link bring-up after both cold boot and system sleep.
