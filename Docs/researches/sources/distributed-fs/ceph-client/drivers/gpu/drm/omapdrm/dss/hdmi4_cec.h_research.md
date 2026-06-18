<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h

## Purpose
`hdmi4_cec.h` is the conditional private interface between the OMAP4 HDMI bridge driver and the HDMI4 CEC implementation. It exposes CEC init, uninit, IRQ, and physical-address update functions when CEC support is enabled, and no-op stubs when `CONFIG_OMAP4_DSS_HDMI_CEC` is disabled.

## Important APIs, types, and functions
The enabled declarations are `hdmi4_cec_set_phys_addr()`, `hdmi4_cec_irq()`, `hdmi4_cec_init()`, and `hdmi4_cec_uninit()`. The disabled branch provides inline no-op or success-returning versions with the same signatures. Forward declarations cover `struct hdmi_core_data`, `struct hdmi_wp_data`, and `struct platform_device`.

## Control flow
`hdmi4.c` can call the functions unconditionally. With CEC enabled, component bind registers a CEC adapter, IRQ handling dispatches core CEC interrupts, EDID or disconnect updates the CEC physical address, and unbind unregisters the adapter. With CEC disabled, those calls compile away and HDMI display/audio operation is unaffected.

## State and persistence
The header itself has no state. In enabled builds, state lives in `hdmi_core_data::adap` and wrapper/core CEC registers. In disabled builds, no CEC state is created and physical address updates are ignored.

## Dependencies and integration points
The header integrates HDMI4 display code with optional media CEC support while keeping non-CEC builds free of CEC runtime dependencies. It depends on Kconfig to choose declarations versus stubs.

## Risks
No-op stubs make disabled CEC builds easy to support, but tests must explicitly cover enabled builds because compile-time success with CEC disabled does not validate register, IRQ, or adapter logic. Callers must not assume `core->adap` is valid unless CEC initialization has run in an enabled build.

## Test signals
Build both `CONFIG_OMAP4_DSS_HDMI_CEC=y` and disabled configurations. Runtime enabled-build signals include CEC adapter creation, IRQ callback dispatch, physical address changes from EDID, and clean adapter unregister. Disabled-build signals are successful HDMI probe/bind and no unresolved CEC symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h -->
