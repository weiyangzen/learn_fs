# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.h

Purpose: declares the i915 FIFO underrun reporting and IRQ handling interface.

Important APIs/types/functions: exposes initialization, CPU/PCH reporting toggles, CPU/PCH IRQ handlers, and immediate CPU/PCH underrun check helpers.

Control flow: no executable code; modeset code uses the toggles to suppress expected underruns and IRQ code uses the handlers for real underruns.

State and persistence: no state in the header; state lives in CRTC flags and hardware interrupt/debug registers.

Dependencies and integration: forward-declares `enum pipe`, `struct intel_crtc`, and `struct intel_display`. Used by display IRQ and modeset code.

Risks: callers must pass CPU pipe vs PCH transcoder consistently. Enabling reporting too early or disabling it without later restoration can hide real watermark failures.

Test signals: compile coverage and modeset/IRQ tests that verify all declared paths are reachable on relevant platforms.
