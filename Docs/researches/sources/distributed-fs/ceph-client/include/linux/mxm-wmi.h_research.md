# sources/distributed-fs/ceph-client/include/linux/mxm-wmi.h

Purpose: declares helper calls for the MXM WMI driver to invoke GPU-adapter-related WMI methods.

Important APIs and types: adapter constants identify discrete and integrated adapters: `MXM_MXDS_ADAPTER_0`, `MXM_MXDS_ADAPTER_1`, and `MXM_MXDS_ADAPTER_IGD`. Functions `mxm_wmi_call_mxds()`, `mxm_wmi_call_mxmx()`, and `mxm_wmi_supported()` expose WMI method invocation and support probing.

Control flow: graphics/platform code checks `mxm_wmi_supported()` and invokes MXDS/MXMX methods for a selected adapter when platform firmware exposes the MXM WMI interface.

State and persistence: no state is stored in the header. Runtime state is firmware/WMI availability and side effects of invoked ACPI methods.

Dependencies and integration points: integrates GPU/ACPI platform handling with the MXM WMI driver. The API is intentionally small and firmware-method oriented.

Risks and test signals: risks include the two discrete adapter constants both being `0x0`, unsupported firmware paths, method side effects that differ by vendor, and missing support checks before calls. Test with systems exposing MXM WMI, unsupported systems, discrete/integrated adapter paths, and error propagation from WMI calls.
