<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h

Purpose: turns a declarative request file into enums, packed big-endian request structs, compile-time offset checks, and perf sysfs event attribute arrays for hypervisor/perf request PMUs.

Important APIs/types/functions: requires `REQUEST_FILE`, `NAME_LOWER`, and `NAME_UPPER`; maps byte widths to `__u8`, `__be16`, `__be32`, and `__be64`; generates `enum <NAME_LOWER>_requests`; generates `struct <NAME_LOWER>_<request>`; defines `<NAME_LOWER>_assert_offsets_correct()` with `BUILD_BUG_ON(offsetof(...))`; emits `PMU_EVENT_ATTR_STRING()` entries for `__count()` fields and two arrays, `hv_gpci_event_attrs_v6` and `hv_gpci_event_attrs`.

Control flow: the same `REQUEST_FILE` is included multiple times with a different set of macros after `_clear.h`: once for enum values, once for structs, once for offset assertions, once for event attributes, once for legacy v6 attribute array, and once for current attribute array. `ENABLE_EVENTS_COUNTERINFO_V6` is undefined before generating the current array so request files can suppress deprecated events for newer firmware.

State and persistence: no runtime mutable state, but it defines static attribute arrays and inline assertions in every includer. Struct layout is ABI-sensitive because fields are big-endian and offset-checked against hypervisor request documentation.

Dependencies and integration: depends on `<linux/perf_event.h>`, perf PMU sysfs macros, request files using `_request-begin.h` conventions, `COUNTER_INFO_VERSION_CURRENT`, and the hv-gpci PMU code that consumes the generated attribute arrays.

Risks and test signals: generated code is macro-heavy; bad offsets, byte sizes other than 1/2/4/8, or stale counter-info gating can break firmware requests or userspace event discovery. Test with compile-time offset assertions, `perf list` for generated events, firmware with counter-info versions <=6 and >=8, and request data parsing on big-endian fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h -->
