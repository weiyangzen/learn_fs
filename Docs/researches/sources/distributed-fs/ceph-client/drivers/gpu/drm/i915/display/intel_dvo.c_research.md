<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c

## Purpose
This file implements support for legacy external DVO transmitter chips attached to older Intel display hardware. It probes known I2C devices, wraps chip-specific operations in DRM encoder/connector callbacks, and programs the DVO port registers for scanout.

## Important APIs, Types, and Functions
The public entry point is `intel_dvo_init()`. Internal state is `struct intel_dvo`, embedding an `intel_encoder`, a copied `intel_dvo_device`, and the attached connector. The known device table covers sil164, ch7xxx, ivch, tfp410, ch7017, and ns2501 variants with addresses and default ports.

Important callbacks include `intel_dvo_get_hw_state()`, `intel_dvo_connector_get_hw_state()`, `intel_dvo_get_config()`, `intel_disable_dvo()`, `intel_enable_dvo()`, `intel_dvo_mode_valid()`, `intel_dvo_compute_config()`, `intel_dvo_pre_enable()`, `intel_dvo_detect()`, `intel_dvo_get_modes()`, `intel_dvo_enc_destroy()`, `intel_dvo_init_dev()`, and `intel_dvo_probe()`.

## Control Flow
Initialization allocates encoder and connector objects, assigns callbacks, probes the device table over GMBUS, initializes DRM encoder/connector objects on success, and sets up LVDS fixed-panel data if needed. Device probing selects a GMBUS pin, forces bit-banging for unstable NAK handling, temporarily enables DVO 2x clock on all pipes for ns2501-style devices, calls chip `init()`, restores DPLL state, and releases bit-banging mode.

Enable flow programs source dimensions and DVO control bits in pre-enable, calls chip `mode_set()`, enables the DVO register, then calls chip DPMS on. Disable calls chip DPMS off, clears `DVO_ENABLE`, and posts the write.

## State and Persistence Behavior
`struct intel_dvo` and its copied device descriptor persist for the encoder lifetime. The chip private state is owned by chip-specific `dev_ops`. Hardware state is split between i915 DVO MMIO registers and external transmitter registers accessed over I2C.

## Dependencies and Integration Points
The file depends on DRM connector/encoder helpers, GMBUS/I2C, chip-specific DVO drivers declared in `intel_dvo_dev.h`, panel fixed-mode helpers, display access checks, DPLL registers for temporary DVO clock enablement, and `intel_dvo_regs.h`.

## Risks
The probe table has overlapping I2C addresses, so probe order matters. Temporarily modifying DPLL DVO 2x mode must always restore original state. DVO type mapping drives connector/encoder type and cloneability. Access checks during suspend or runtime PM must avoid I2C/MMIO access when display hardware is unavailable.

## Test Signals
Signals include detection logs for supported chips, successful DDC or panel mode enumeration, mode validation through chip-specific callbacks, enable/disable DPMS sequencing, LVDS fixed-mode setup, hotplug polling for TMDS devices, and no DPLL state regression after failed probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c -->
