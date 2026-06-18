# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tc.h

Purpose: defines the public Type-C display-port interface and the stable hardware-mapped pin-assignment enum. It is consumed by DDI, DP, hotplug, modeset, debugfs, and power-management code.

Important APIs and types: `enum intel_tc_pin_assignment` values must match PORT_TX_DFLEXPA1 and TCSS_DDI_STATUS fields. The comments document DP/USB lane use, cable types, and DP-alt standards. Query helpers report TC mode, HPD-glitch behavior, connection usability, max lanes, and pin assignment. State-management helpers initialize and sanitize modes, lock/unlock the port, get/put link references, check/cancel/schedule link resets, suspend, init/cleanup, and print debug info.

Control flow and integration: callers bracket operations that need a usable PHY with `intel_tc_port_lock()`/`unlock()` or longer-lived `get_link()`/`put_link()`. Modeset readout calls init/sanitize. Hotplug/link code uses `intel_tc_port_connected()` and reset helpers. Power code uses `intel_tc_cold_requires_aux_pw()` to decide whether AUX power blocks TC-cold.

State and persistence: state is opaque in `intel_tc.c`; this header exposes only stable queries and operations. The pin-assignment enum is effectively persistent ABI to register fields and should not be renumbered.

Risks and tests: changes can break TC mode arbitration, lane negotiation, or build-time users. Test signals include compiling all users, exercising each mode query, validating lane counts for pin C/D/E on DP2 platforms and legacy ICL assignments, suspend/resume, and DP-alt hot-unplug link reset behavior.
