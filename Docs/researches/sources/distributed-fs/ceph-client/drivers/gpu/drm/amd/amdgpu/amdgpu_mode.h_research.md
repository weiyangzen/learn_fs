## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mode.h

Purpose: defines AMDGPU display/KMS private types and constants for CRTCs, connectors, encoders, framebuffers, I2C/DDC, HPD, audio, color properties, pageflip/vblank state, and display function callbacks.

Important APIs/types: container macros convert DRM objects to AMDGPU private structs. Enums define scaling, underscan, HPD pins, CRTC/vline IRQ IDs, pageflip IRQ IDs, and flip status. `struct amdgpu_i2c_bus_rec` captures Atom GPIO/I2C bus register metadata; `struct amdgpu_pll` stores clock limits/flags; `struct amdgpu_display_funcs` is the display backend vtable. `struct amdgpu_mode_info` is the central display state holder with Atom context, CRTC/plane/audio arrays, properties, color-management properties, backlight, firmware flags, and display function table. `struct amdgpu_crtc`, `amdgpu_encoder`, `amdgpu_connector`, and `amdgpu_mst_connector` extend DRM objects with AMD-specific state.

Control flow contract: display initialization populates `amdgpu_mode_info`, creates properties, links encoders/connectors, installs display funcs, and uses the declared helpers for DDC probing, scanout position, page flip, CRTC config, connector lookup, and mode fixups. KMS vblank code in `amdgpu_kms.c` relies on CRTC arrays and scanout flags from this header.

State and persistence: all structures are runtime DRM/KMS state. Some fields cache BIOS-derived data, EDID, backlight level, audio pin status, color properties, pageflip work, and writeback state. No durable persistence is defined here.

Dependencies/integration: includes DRM CRTC/encoder/framebuffer/probe helpers, DisplayPort/MST helpers, Linux I2C/hrtimer, AMD freesync modules, DM IRQ params, and idle state manager. It bridges legacy Atom display and DC/DM display paths.

Risks: many fields are shared between IRQ handlers, modeset paths, and atomic/display code, so locking and lifetime rules are external and critical. Fixed maximum arrays for CRTCs/planes/HPD/AFMT must match hardware limits. Color-management property semantics must stay ABI-compatible with DRM userspace.

Test signals: modeset and pageflip tests, HPD connect/disconnect, MST topology, DDC/AUX probing, vblank counter accuracy, backlight/audio properties, writeback, color-management property tests, and compile coverage for DC/non-DC configurations.
