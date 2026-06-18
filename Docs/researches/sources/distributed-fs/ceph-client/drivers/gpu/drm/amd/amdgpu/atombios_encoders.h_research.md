# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atombios_encoders.h

Purpose: declares the AtomBIOS encoder API used by AMDGPU display code. It is the public header for the legacy AtomBIOS display-encoder implementation in `atombios_encoders.c`.

Important APIs and types: exposes backlight accessors and lifecycle (`get_backlight_level_from_reg`, `set_backlight_level_to_reg`, `get_backlight_level`, `set_backlight_level`, `init_backlight`, `fini_backlight`), encoder classification and mode helpers (`is_digital`, `mode_fixup`, `get_encoder_mode`), DIG/DAC/display sequencing (`setup_dig_encoder`, `setup_dig_transmitter`, `set_edp_panel_power`, `dpms`, `set_crtc_source`, `init_dig`), detection and scratch state (`dac_detect`, `dig_detect`, `setup_ext_encoder_ddc`, `set_bios_scratch_regs`), and private-data constructors (`get_lcd_info`, `get_dig_info`). The key return types are DRM connector status and `struct amdgpu_encoder_atom_dig *`.

Control flow: this header does not implement control flow, but its declarations define the display stack call graph: connector/encoder setup code obtains DIG/LCD private data, mode-setting calls fixup and CRTC-source programming, DPMS calls the AtomBIOS encoder/transmitter sequence, connector detection calls DAC/DIG detect, and driver teardown calls backlight finalization.

State and persistence: declared functions mutate hardware registers, AtomBIOS scratch registers, backlight devices, connector detect state, and `amdgpu_encoder_atom_dig` private state. The header itself is stateless.

Dependencies and integration points: consumers must already know DRM and AMDGPU core types (`struct drm_encoder`, `struct drm_connector`, `struct drm_display_mode`, `struct amdgpu_device`, `struct amdgpu_encoder`, and `struct amdgpu_encoder_atom_dig`). It integrates the AtomBIOS display path with the rest of AMDGPU mode-setting and connector setup.

Risks: the header relies on prior type declarations from including translation units rather than including all defining headers itself. Prototype drift against `atombios_encoders.c` would break display builds. The API surface exposes many low-level sequencing operations, so callers must preserve ordering and valid encoder/connector associations.

Test signals: compile all AMDGPU display objects that include this header. Link success confirms implementation/prototype alignment. Runtime display tests exercise the declared entry points indirectly through mode set, DPMS, hotplug detection, and backlight lifecycle.
