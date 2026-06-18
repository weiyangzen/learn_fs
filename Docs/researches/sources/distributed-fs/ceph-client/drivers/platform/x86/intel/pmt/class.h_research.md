# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.h

Purpose: defines the PMT class-layer data structures and APIs shared by telemetry, discovery, crashlog, and PMC integration code.

Important APIs/types/functions: access-type macros `ACCESS_BARID` and `ACCESS_LOCAL` plus `GET_BIR()`/`GET_ADDRESS()` decode PMT base-offset fields. `struct telem_endpoint` represents a telemetry endpoint with device, header, callbacks, MMIO base, presence flag, and kref. `struct intel_pmt_header` is the decoded discovery header. `struct intel_pmt_entry` stores one class device/resource. `struct intel_pmt_namespace` supplies namespace name, xarray, header decoder, and optional endpoint registration hook. Declared APIs include `pmt_telem_read_mmio()`, `intel_pmt_is_early_client_hw()`, `intel_pmt_dev_create()`, `intel_pmt_dev_destroy()`, and optionally `intel_pmt_get_features()`.

Control flow: feature drivers include this header, fill an entry/namespace, and delegate common device creation/destruction to `class.c`. Telemetry endpoint users rely on `struct telem_endpoint` from this header through `telemetry.h`.

State and persistence: no header state. It defines the per-entry and per-endpoint state layout used for module lifetime by PMT drivers.

Dependencies and integration points: depends on `linux/intel_vsec.h`, xarray, IO helpers, and `telemetry.h`. It bridges class code with telemetry feature discovery and crashlog.

Risks: `struct intel_pmt_entry` has many ownership-sensitive fields; feature drivers must not destroy class-managed objects out of order. Conditional `intel_pmt_get_features()` stub means discovery-disabled builds silently omit feature enrichment.

Test signals: compile matrix with discovery enabled/disabled validates the conditional stub. PMT telemetry/crashlog probes validate namespace and entry layout.
