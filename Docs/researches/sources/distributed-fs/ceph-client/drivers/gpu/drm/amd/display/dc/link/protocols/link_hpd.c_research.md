# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_hpd.c

Purpose: provides basic HPD state, enable/disable, filter programming, and GPIO-to-HPD-source discovery. It intentionally avoids higher-level detection policy.

Important APIs/functions: `link_get_hpd_state`, `link_enable_hpd`, `link_disable_hpd`, `link_enable_hpd_filter`, `program_hpd_filter`, `link_get_hpd_gpio`, and `get_hpd_line`.

Control flow: HPD state and enable/disable delegate to `link_enc->funcs` when a link encoder exists. Filter enable updates `link->is_hpd_filter_disabled` and programs per-signal connect/disconnect delays: HDMI/DVI get 500/100 ms, DP/MST get 80/0 ms, and eDP/LVDS/default skip filtering. GPIO discovery reads BIOS HPD info and GPIO pin info, creates an IRQ GPIO, maps IRQ source to `HPD_SOURCEID*`, and destroys the temporary GPIO.

State/persistence: mutates `link->is_hpd_filter_disabled`; otherwise it is a facade over encoder and GPIO-service state.

Dependencies/integration: depends on `gpio_service_interface`, `dc_bios`, link encoder function tables, and IRQ source definitions. `link_hpd.h` also declares DPIA HPD query, implemented elsewhere.

Risks: missing `link_enc` means false/no-op behavior; filter programming asserts in one disabled path. GPIO fallback is only used for DCE/DCN versions up to 4.01, so newer paths depend on encoder mapping.

Test signals: HPD high/low query, filter delay programming per connector type, BIOS GPIO mapping to HPD source IDs, no-link-encoder safety, and MST/SST switch behavior with DP filter timing.
