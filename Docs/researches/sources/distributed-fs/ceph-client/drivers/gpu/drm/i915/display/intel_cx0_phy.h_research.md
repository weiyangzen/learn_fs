# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy.h

Purpose: public interface for CX0 PHY/PLL operations, message-bus access, signal level programming, TBT clock handling, powerdown sequencing, and verification hooks.

Important APIs: the header exposes low-level message-bus helpers (`intel_cx0_read`, `write`, `rmw`, `wait_for_ack`, `bus_reset`, `clear_response_ready_flag`), PLL lifecycle helpers (`intel_cx0pll_calc_state`, `readout_hw_state`, `calc_port_clock`, `dump_hw_state`, `compare_hw_state`, `verify_plls`), MTL PLL/TBT clock wrappers, lane count readout, C10 PHY detection, signal-level setup, powerdown helpers, ALPM LFPS helper, and power-save workaround. It also defines `MB_WRITE_COMMITTED` and `MB_WRITE_UNCOMMITTED` boolean aliases used for message-bus writes.

Control flow and state: the header is declarative only. Callers must use these APIs in contexts where display power and encoder state are valid; the implementation handles PSR pause/DC-off for most PHY transactions.

Dependencies and integration: forward declarations keep DDI, DPLL manager, link training PHY, HDMI, reset, and display init code from including the large implementation headers. It depends on Linux integer types for `u8`/`u32`.

Risks: the header currently contains a duplicate declaration of `intel_mtl_pll_disable_clock()`. It also declares `intel_cx0_phy_check_hdmi_link_rate()` and `intel_cx0_is_hdmi_frl()`, but a display-tree search in this snapshot found declarations only and no implementation, so consumers would fail to link if these APIs are referenced unless implemented outside the searched scope. The raw read/write helpers are powerful and must not be called without respecting transaction/power sequencing.

Test signals: compile/link coverage for all declared APIs, plus DPLL manager and link-training call paths that exercise the raw and high-level CX0 operations.
