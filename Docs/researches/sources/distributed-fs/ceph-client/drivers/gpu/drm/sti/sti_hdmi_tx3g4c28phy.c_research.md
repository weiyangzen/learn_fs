# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.c

Purpose: Provides PHY-specific start/stop operations for the TX3G4C28 HDMI serializer/PLL used by STiH407 HDMI.

Important APIs/functions: `sti_hdmi_tx3g4c28phy_start()` selects PLL input/output divider values for the requested pixel clock, programs PLL control, waits for DLL lock through the HDMI wait event, then programs serializer configuration, current control, and calibration registers. `sti_hdmi_tx3g4c28phy_stop()` keeps detection bits, clears PLL config, waits for lock deassertion, and logs if the PLL remains locked. `tx3g4c28phy_ops` exposes these hooks to `sti_hdmi.c`.

Control flow: Start rejects unsupported input clocks and TMDS clocks above 340 MHz. Divider selection is table-driven; source termination is enabled above 165 MHz. A board/SoC PHY config table optionally overrides external bits while internal control bits are masked out.

State/persistence: Uses `hdmi->mode.clock` and `hdmi->event_received` wait synchronization. It does not own separate allocated state.

Dependencies/integration: Depends on `hdmi_read()`/`hdmi_write()`, `struct sti_hdmi`, HDMI status bits, and interrupts from the HDMI controller to wake waiters for PLL lock transitions.

Risks/test signals: If HDMI interrupts are disabled or lost, start/stop wait until timeout and status polling decides success. Config table covers only up to 300 MHz despite a 340 MHz TMDS upper guard; higher clocks fall back to default serializer settings. Test clock ranges, PLL lock timeout, 165 MHz termination boundary, and bridge disable lock deassertion.
