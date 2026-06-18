# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_connector.c

Purpose: Implements DRM connector objects for Nouveau, including detection, EDID acquisition, LVDS/eDP fallbacks, connector properties, mode enumeration/validation, hotplug handling, DP AUX transfer, and connector creation from nvif or legacy DCB data.

Important APIs/functions: `nouveau_connector_create()`, `nouveau_connector_hpd()`, `nouveau_conn_native_mode()`, `nouveau_conn_attach_properties()`, connector atomic property get/set/duplicate/destroy/reset functions, `find_encoder()`, and `nouveau_conn_mode_clock_valid()` via the header. Internal logic includes DDC/OF/LVDS detection, EDID ownership, forced encoder selection, scaler mode injection, depth detection, late/early register, hotplug/IRQ event callbacks, AUX transfer, and DCB-to-DRM connector type mapping.

Control flow: Detection resumes or keeps runtime PM active, probes DP/nvif output status or I2C DDC, fetches EDID through I2C or nvif, corrects DVI-I encoder type from EDID digital bit, falls back to Open Firmware EDID, then analog/TV load detection when forced. LVDS detection tries DDC, ACPI EDID, VBIOS hardcoded panel mode, and embedded EDID, then applies lid status. Mode enumeration adds EDID modes or VBIOS native mode, computes native mode/depth, asks TV encoders for modes, and adds scaler modes for fixed panels.

State/persistence: `struct nouveau_connector` stores DCB connector type/index, nvif connector/event handles, hotplug pending bits, DP AUX, DP encoder, detected encoder, EDID, native mode, backlight, and connector property state. Module parameters control TV detection, lid handling, dual-link TMDS, and HDMI max clock.

Dependencies/integration: Uses DRM connector/helpers/atomic/EDID/DP AUX, runtime PM, ACPI lid/video, vga_switcheroo, Nouveau BIOS, display properties, encoder helpers, DP link functions, and nvif connector/output APIs.

Risks/test signals: Detection spans power management and hotplug work, so runtime PM imbalance or polling deadlocks are key risks. EDID ownership and native mode replacement must avoid leaks. Mode validation depends on hardware generation, HDMI caps, DCB max frequency, and DP link limits. Test with DVI-I analog/digital, DP MST/SST, eDP/LVDS panels without EDID, ACPI lid events, hotplug IRQs, property changes causing modesets, and HDMI clock overrides.
