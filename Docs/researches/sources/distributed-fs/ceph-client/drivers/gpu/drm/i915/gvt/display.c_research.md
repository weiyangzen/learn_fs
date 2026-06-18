# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/display.c

Purpose: emulates virtual display presence, DP EDID/DPCD data, hotplug state, vblank interrupts, display register state, and reset/cleanup for GVT vGPUs.

Important APIs/types/functions: public entry points are `intel_vgpu_init_display()`, `intel_vgpu_reset_display()`, `intel_vgpu_clean_display()`, `intel_vgpu_emulate_vblank()`, `vgpu_update_vblank_emulation()`, `intel_vgpu_emulate_hotplug()`, and `pipe_is_enabled()`. Internal helpers include `get_edp_pipe()`, `edp_pipe_is_enabled()`, `setup_virtual_dp_monitor()`, `clean_virtual_dp_monitor()`, `emulate_monitor_status_change()`, `vblank_timer_fn()`, and `emulate_vblank_on_pipe()`.

Control flow: init initializes I2C EDID support, selects a virtual DP port by platform, allocates EDID/DPCD state, seeds fixed EDID and DP 1.2 DPCD data, configures a vblank hrtimer period from refresh rate, and programs virtual display registers to signal a monitor. Vblank timer callbacks request GVT service, which later increments frame counters and triggers vblank/flip-done virtual events under `vgpu_lock`. Hotplug emulation toggles platform-specific virtual ISR/IIR/fuse/hotplug registers and triggers the matching virtual event.

State and persistence: per-port `edid`, `dpcd`, type, resolution id, refresh rate, `vgpu->display.port_num`, and `vgpu->vblank_timer` persist for the vGPU lifetime. Virtual MMIO state is stored in vGPU register arrays and reset by `emulate_monitor_status_change()`.

Dependencies and risks: depends on i915 display register definitions, platform predicates, hrtimers, GVT event service, EDID helpers, and vGPU virtual register accessors. Risks include platform-specific register drift, fixed M/N timing values, unhandled ports/pipes, hrtimer cancellation races, allocation unwind leaks, and mismatched hotplug status bits. Test signals include guest detecting the expected virtual monitor, vblank and flip events firing only for enabled pipes, hotplug connect/disconnect interrupts, cleanup cancelling timers and freeing EDID/DPCD, and reset restoring display presence.
