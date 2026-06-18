# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.h

Purpose: declares GMBUS pin identifiers and the public GMBUS adapter/control API.

Important APIs/types/functions: defines legacy and platform-specific pin constants such as `GMBUS_PIN_VGADDC`, `GMBUS_PIN_DPB`, `GMBUS_PIN_1_BXT`, Type-C pins, and `GMBUS_NUM_PINS`. Declares setup/teardown, valid-pin check, adapter lookup, forced bit-banging controls, controller reset, HDCP Aksv output, and IRQ handler.

Control flow: no executable code; display connector code uses pin constants to obtain adapters and DDC/HDCP code uses the exported transfer controls.

State and persistence: no state is defined here. Adapter arrays and force-bit state are owned by `intel_gmbus.c`.

Dependencies and integration: forward-declares `i2c_adapter` and `intel_display`; consumed by connector/DDC/HDCP/display setup code.

Risks: pin constants are reused differently across platform generations, so callers must use platform-appropriate pin assignments from VBT/connector setup.

Test signals: compile connector code using each pin family and verify invalid pins are rejected at runtime.
