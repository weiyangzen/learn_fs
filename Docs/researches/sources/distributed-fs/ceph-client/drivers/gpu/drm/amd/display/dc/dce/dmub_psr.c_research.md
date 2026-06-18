# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dmub_psr.c

Purpose: implements the DMUB-backed Panel Self Refresh control object: PSR state query, version programming, enable/disable, level/power optimization, sink vtotal, settings copy, force-static, and residency query.

Important functions: `dmub_psr_get_state()` uses GPINT and `convert_psr_state()` to translate firmware raw state values to `enum dc_psr_state`. `dmub_psr_enable()` sends enable/disable then optionally waits up to about 500 ms using `udelay(500)` loops. `dmub_psr_copy_settings()` gathers pipe/link/PSR context, programs link encoder fast training and secondary packet registers, fills `dmub_cmd_psr_copy_settings_data`, and sends it to firmware. Other command helpers set PSR version, level, sink vtotal, power options, force static, and residency.

Control flow: copy settings first locates the active eDP pipe in current resource context, rejects missing pipe or unsupported PSR version, programs link encoder state, then sends hardware instance IDs and many policy/debug flags to DMUB. It includes sink-specific workarounds for DSC/FEC/TPS3 wakeup, FFU mode, vertical poweroff line, and relock delay. Enable/disable and level commands are guarded by firmware state where needed.

State and persistence: `struct dmub_psr` stores context and function table only. PSR runtime state is firmware-owned and queried by GPINT. Link settings, DPCD caps, debug flags, FEC/DSC state, and current pipe context are copied into firmware context and persist there until replaced or disabled.

Dependencies and integration: depends on `dc_dmub_srv`, DMUB command/GPINT infrastructure, `core_types`, link encoder PSR callbacks, DPCD capabilities, current DC state, and DC debug options. It integrates with eDP link power management and commit sequencing.

Risks: current implementation scans a fixed `MAX_PIPES=6` and notes multi-eDP refactor TODOs. Long retry loops can assert on firmware non-response. Sink-specific byte-string workarounds are brittle but necessary. `dmub_psr_force_static()` assigns payload bytes through the enable union member, which is fragile. Test signals include PSR1 and PSR SU1 setup, GPINT timeout handling, DSC/FEC sink workarounds, force-FFU behavior, residency modes, high-IRQ wait constraints, and no-pipe rejection.
