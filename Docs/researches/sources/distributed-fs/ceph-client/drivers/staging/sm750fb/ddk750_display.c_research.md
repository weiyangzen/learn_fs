# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_display.c

Purpose: programs SM750 logical display output routing, timing/plane enable state, panel power sequencing, DAC, and DPMS through register operations.

Important APIs/types/functions: public `ddk750_set_logical_disp_out(enum disp_output output)` applies bit-encoded output selections. Internal helpers are `set_display_control()`, `primary_wait_vertical_sync()`, and `sw_panel_power_sequence()`.

Control flow: the public function checks usage bits in the `disp_output` value and conditionally updates panel path, CRT path, primary timing/plane, secondary timing/plane, panel sequence, DAC power, and DPMS. Enabling display timing turns on timing before plane and repeatedly writes until non-reserved bits match. Panel power sequencing toggles FPEN, DATA, and VBIASEN with vertical-sync waits.

State and persistence: display routing and power state persist in `PANEL_DISPLAY_CTRL`, `CRT_DISPLAY_CTRL`, `SYSTEM_CTRL`, and `MISC_CTRL` registers. The function has no software state.

Dependencies and integration: uses register definitions, `peek32()`/`poke32()`, `set_DAC()` macro from `ddk750_power.h`, and `ddk750_set_dpms()`. Called by higher-level framebuffer output setup.

Risks: vertical-sync waits poll hardware and can stall if guard checks miss a bad state, though the helper skips waiting when PLL/timing is off. The panel sequence uses OR-only updates for enable bits, so off sequencing may not clear fields as expected. Encoded enum values combine data and usage masks, making invalid combinations possible.

Test signals: route LCD/CRT outputs through primary/secondary paths, toggle timing/plane on and off, verify DAC/DPMS bits, test with PLL off, and read back register values after repeated writes.
