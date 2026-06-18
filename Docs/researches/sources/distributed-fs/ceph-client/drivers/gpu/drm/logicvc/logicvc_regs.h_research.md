# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_regs.h

Purpose: defines LogiCVC register offsets and bitfields used by core, CRTC, layer, interface, and IRQ code.

Important APIs/types/functions: timing registers, `LOGICVC_CTRL_*`, `LOGICVC_INT_*`, `LOGICVC_POWER_CTRL_*`, IP version masks, layer register macros, buffer select encoding, alpha/control bits, and maximum dimension constants.

Control flow: no code flow. Runtime modules use these macros to program modes, layers, interrupts, video power, and version/capability detection.

State and persistence: hardware register layout and bit semantics are encoded as compile-time constants.

Dependencies and integration points: consumed with regmap operations across the LogiCVC driver. Requires bit helper macros from included kernel environment.

Risks and test signals: `LOGICVC_LAYER_ADDRESS_REG` and `LOGICVC_LAYER_HOFFSET_REG` intentionally share offset for different IP modes; misuse can program wrong addressing path. Test register writes under both caps variants, vblank IRQ mask/stat handling, and plane enable/disable.
