# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display.h

## Purpose
`intel_display.h` is the broad public display header for the i915 display subsystem. It provides stable naming helpers, display topology iteration macros, atomic state iteration wrappers, and declarations for modeset, pipe, plane, transcoder, encoder, M/N timing, power-domain, and state-checking functions implemented elsewhere. It is not an implementation file; its main persistence effect is the contract it imposes on enum values, list ownership, and state traversal patterns used throughout the display stack.

## Important APIs, Types, And Functions
The file defines `pipe_name()`, `transcoder_name()`, `transcoder_is_dsi()`, `plane_name()`, `port_identifier()`, `port_name()`, and `phy_name()` for consistent diagnostics. It introduces `enum tc_port`, `enum phy`, and `enum phy_fia`, building on display limits. The numerous `for_each_*` macros are central APIs: they walk pipes, ports, PHYs, DBUF slices, CRTCs, planes, encoders, DP encoders, connectors, and old/new DRM atomic state entries. The declaration set exposes `intel_atomic_check()`, `intel_atomic_commit()`, `intel_mode_valid()`, pipe config read/compare, joiner helpers, transcoder enable/disable, M/N register helpers, encoder/PHY mapping, FIFO underrun arming, pipe bpp limits, modeset power-domain acquisition/release, initial commit, and assertions.

## Control Flow And State
Control flow is macro-driven. Iterators combine DRM lists, i915 `display->pipe_list`, runtime masks from `DISPLAY_RUNTIME_INFO()`, and atomic state arrays. Joiner and modeset order macros deliberately walk primary and secondary pipe masks in different directions for disable and enable sequencing. The header assumes pipe and transcoder numbering from `intel_display_limits.h`, and many macros depend on `struct intel_display` runtime masks being initialized before use. `INTEL_DISPLAY_STATE_WARN()` converts display state mismatches into either `drm_WARN()` or `drm_err()` based on the `verbose_state_checks` parameter.

## Dependencies And Integration Points
This header integrates DRM atomic/mode APIs with i915 display objects from `intel_display_types.h`, runtime device info from `intel_display_device.h`, and register abstractions through `i915_reg_defs.h`. It is included by low-level modeset, plane, encoder, connector, and IRQ code that needs shared topology traversal. `to_intel_display(dev)` and list layout are expected to be valid for all iterator users.

## Risks And Test Signals
The main risks are macro side effects, stale runtime masks, and assumptions that pipe/transcoder enum values remain stable. Bugs show up as missed modesets, wrong pipe order for joiner modes, invalid state comparisons, or warnings from `INTEL_DISPLAY_STATE_WARN()`. Useful tests include DRM atomic KMS tests, joiner/bigjoiner/ultrajoiner modes, pipe-fused platforms, MST/DP encoder enumeration, and state-checker logs during boot, suspend/resume, and fastset commits.
