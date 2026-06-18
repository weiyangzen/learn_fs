# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.c

Purpose: This file implements x86-specific evsel behavior for sampling weight, topdown grouping support, hardware event naming, automatic counter reset masks, AMD IBS warnings/errors, and Intel topdown open-error diagnostics.

Important APIs, types, and functions: `arch_evsel__set_sample_weight()` requests `WEIGHT_STRUCT`. `evsel__sys_has_perf_metrics()` checks that system topdown metrics exist and the evsel PMU type is `PERF_TYPE_RAW`. `arch_evsel__must_be_in_group()` returns true for topdown slots or metrics on supporting PMUs. `arch_evsel__hw_name()` formats hardware event names with optional PMU prefix. `arch_evsel__apply_ratio_to_prev()` sets `config2` ACR masks across a ratio event and its previous event. `arch__post_evsel_config()` warns once for AMD IBS L3-miss-only sampling-period skew. `arch_evsel__open_strerror()` dispatches to AMD IBS or Intel topdown-specific error explanation.

Control flow: Topdown helpers first gate on `topdown_sys_has_perf_metrics()` and PMU lookup. Hardware naming extracts event and PMU bits from `attr.config`. Ratio application verifies PMU `acr_mask` format support, finds the previous evsel, ensures previous `config2` is unused, computes masks from group index, and writes both attrs. Post-config warning exits unless AMD, finds IBS PMUs, checks L3-miss bits, and prints once. Open-error formatting emits AMD privilege-filter guidance for precise IBS events, or Intel topdown messages for invalid slots leadership or duplicate metric events.

State and persistence: The file mutates in-memory `perf_event_attr` fields, evsel sample bits, and one static `warned_once` flag. It emits warnings/errors but writes no persistent files. Its behavior affects subsequent `perf_event_open()` calls through attr configuration and error text.

Dependencies and integration points: It integrates with generic evsel configuration (`util/evsel.c` weak arch hooks), PMU format helpers, x86 CPU detection (`env.h`), topdown helpers, evlist formatting, and stat configuration. AMD IBS constants define config bits for `ibs_fetch` and `ibs_op`. Intel diagnostics depend on evsel group relationships and topdown event identity helpers.

Risks: ACR mask computation is group-index-sensitive and can misconfigure reset-on-overflow behavior if event order changes. The topdown PMU check assumes raw PMU type identifies the core PMU. Error messages must not mask unrelated `EINVAL` causes. The AMD warning is intentionally once-per-process, so later affected evsels will not repeat the message.

Test signals: Topdown `perf stat` groups should open with slots as leader and no duplicate metric events. AMD IBS commands with unsupported privilege filters should show the tailored message. IBS L3-miss-only sampling should print the skew warning once. Hardware event names should include PMU names on hybrid platforms.
