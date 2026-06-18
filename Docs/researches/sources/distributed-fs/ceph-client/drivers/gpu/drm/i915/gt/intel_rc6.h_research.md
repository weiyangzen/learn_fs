<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h

Purpose: declares RC6 lifecycle, parking, residency, and BIOS-state query functions.

Important APIs: `intel_rc6_init/fini`, `intel_rc6_sanitize`, `intel_rc6_enable/disable`, `intel_rc6_unpark/park`, `intel_rc6_residency_ns/us`, `intel_rc6_print_residency`, and `intel_check_bios_c6_setup`.

Control flow: GT power-management code initializes RC6, enables it when hardware state is ready, calls unpark/park as GT busy-idle state changes, sanitizes after resume/reset, queries residency for telemetry, and finalizes during teardown.

State and persistence: state is carried by `struct intel_rc6` from `intel_rc6_types.h`; this header does not define fields.

Dependencies and integration points: uses Linux integer types and forward declarations for `seq_file` and RC6 types. Integrated with GT PM, debugfs, runtime PM, and platform BIOS validation.

Risks: callers must pair init/fini and enable/disable to keep runtime-PM references balanced. Residency queries return zero when unsupported.

Test signals: GT PM tests, residency debugfs tests, suspend/resume sanitize, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6.h -->
