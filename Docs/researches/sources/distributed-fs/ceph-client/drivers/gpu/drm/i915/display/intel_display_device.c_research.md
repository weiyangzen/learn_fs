# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_device.c

## Purpose
`intel_display_device.c` maps PCI devices and display IP versions to i915 display capabilities, platform flags, subplatform flags, stepping information, static device info, and runtime display masks. It is the display capability database and probe-time detector for legacy PCI-ID platforms and newer GMD-ID based platforms.

## Important APIs, Types, And Functions
Public APIs are `intel_display_device_probe()`, `intel_display_device_remove()`, `intel_display_device_info_runtime_init()`, `intel_display_device_info_print()`, `intel_display_device_present()`, and `intel_display_device_enabled()`. Internal descriptors include `struct platform_desc`, `struct subplatform_desc`, and `struct stepping_desc`. The file defines many `intel_display_device_info` instances and macros for pipe/transcoder/cursor register offsets, color LUT capabilities, DBUF sizes, feature flags, runtime defaults, FBC masks, and port masks. `probe_gmdid_display()` reads `GMD_ID_DISPLAY` from MMIO for GMD-ID devices. `get_pre_gmdid_step()` maps PCI revision IDs to symbolic display steppings.

## Control Flow And State
Probe allocates `struct intel_display`, stores the DRM backpointer and parent interface, copies display params, rejects known no-display SKUs, finds the platform descriptor by PCI ID, optionally probes GMD ID, copies static runtime defaults, merges subplatform flags, initializes stepping, and logs the detected display version. Runtime init then mutates `DISPLAY_RUNTIME_INFO()` based on fuses, workarounds, platform restrictions, scaler/sprite counts, pipe disables, HDCP/DMC/DSC disable straps, DBUF overlap capability, eDP-on-TypeC support, and rawclk readout. If display is absent or fused off, runtime info is zeroed and DRM modeset/atomic features are disabled.

## Dependencies And Integration Points
The file depends on PCI ID macros, display register definitions, `intel_de` MMIO access, display power, opregion headless detection, display workarounds, FBC IDs, color management constants, and display params. Its outputs drive almost every `HAS_*`, `DISPLAY_VER*`, port, pipe, transcoder, scaler, sprite, and feature check used by modeset, IRQ, debugfs, power, PSR, FBC, and watermark code.

## Risks And Test Signals
The largest risk is incorrect platform data: wrong masks or offsets cause missing connectors, invalid register programming, disabled features, or use of fused-off resources. GMD-ID probing can fail if MMIO mapping fails or an unknown display release is encountered, disabling display. Step-map gaps deliberately choose a later or future step, which may affect workaround selection. Test signals include boot logs with detected display version/stepping, `intel_display_caps`, connector enumeration, pipe-fused SKU tests, GMD-ID platform bring-up, rawclk sanity, and KMS coverage across old GMCH through Xe2/Xe3 platforms.
