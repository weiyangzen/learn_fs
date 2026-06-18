# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/grph_object_ctrl_defs.h

Purpose: Defines BIOS/control-plane data structures shared between ATOM BIOS parsing, ASIC control, and other DAL components. It describes display devices, I2C/HPD info, embedded panel timings, firmware clocks, spread spectrum, encoder capabilities, DDI channel mapping, integrated system info, HDMI retimer settings, eDP info, and backlight boundaries.

Important APIs and types: Key types include `enum display_output_bit_depth`, `enum dal_device_type`, `struct device_id`, `struct graphics_object_i2c_info`, `struct graphics_object_hpd_info`, `struct device_timing`, `struct embedded_panel_info`, `struct dc_firmware_info`, `struct spread_spectrum_info`, `struct graphics_object_encoder_cap_info`, `union ddi_channel_mapping`, `struct transmitter_configuration`, `struct ext_hdmi_settings`, `struct edp_info`, `struct integrated_info`, and `struct panel_backlight_boundaries`.

Control flow: This is a passive schema. BIOS parsing fills these structures, then display resource/link/power code consumes them to determine connector routing, DDC/HPD registers, panel timings, spread spectrum parameters, PLL limits, eDP power sequencing, external HDMI settings, and backlight limits.

State and persistence: Many fields mirror firmware/BIOS tables and therefore persist across driver runtime as cached hardware descriptors. Several bitfields encode firmware flags and timing polarities. Fake EDID data is represented by size plus pointer, so lifetime must be managed by the producer.

Dependencies and integration points: Includes `grph_object_defs.h`, which supplies object IDs and transmitter enums. Integrates with BIOS parser interfaces, link encoder setup, DDC/HPD service setup, panel power sequencing, spread-spectrum clock programming, and board connector layout logic.

Risks: Structures encode hardware contracts and versioned firmware layouts; incorrect packing, field interpretation, or unit conversion can misprogram clocks, power sequences, or connector mapping. `integrated_info` is large and version-accumulated, with comments marking V6/V7/V9/V11/V2.1 additions, so consumers must know which fields are valid. Pointers like `fake_edid` require lifetime discipline.

Test signals: Validate BIOS table parsing with golden firmware blobs, DDI lane mapping, panel timing/polarity extraction, spread spectrum units, eDP delay units, backlight boundary handling, and external HDMI register sequences.
