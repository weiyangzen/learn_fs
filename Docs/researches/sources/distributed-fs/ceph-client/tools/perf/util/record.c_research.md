# sources/distributed-fs/ceph-client/tools/perf/util/record.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/record.c` implements shared perf record option configuration helpers. It normalizes sampling frequency/period, configures evlists/evsels for recording, handles leader sampling rules, chooses sample-id formats, tests event selectability, and parses `-F/--freq` style frequency options.

## Important APIs, Types, and Functions

Public functions are `evlist__config`, `record_opts__config`, `evlist__can_select_event`, and `record__parse_freq`. Internal helpers include `evsel__read_sampler`, `evsel__config_term_mask`, `evsel__config_leader_sampling`, `get_max_rate`, and `record_opts__config_freq`.

## Control Flow

`evlist__config` sets `no_inherit` when no user CPU is requested, detects `comm_exec` support, configures each evsel with `evsel__config`, sets tracking comm-exec where possible, then applies leader sampling adjustments after sample types are known. It enables sample identifiers when full auxtrace or explicit sample identifiers are requested, or when multi-event evlists have divergent sample types, then computes id positions.

Leader sampling handles grouped events where the group leader samples reads. If the leader is an AUX event, topdown sample-read event, or mem-loads AUX event, the sampler is the next group member. Non-sampler members without explicit frequency/period terms have sampling disabled and inherit sampler/leader sample type bits so synthesized group samples can be reported consistently.

`record_opts__config_freq` rejects simultaneous user frequency and period, folds user-provided values into defaults, refuses zero frequency/period, reads `kernel/perf_event_max_sample_rate`, throttles or rejects over-limit frequencies depending on `strict_freq`, and clamps defaults. `evlist__can_select_event` parses a temporary event, chooses a CPU, tries `perf_event_open`, retries with pid 0 on `EACCES` from pid -1, and returns true if an fd can be opened. `record__parse_freq` accepts `"max"` or numeric strings and stores `user_freq`.

## State and Persistence Behavior

The file mutates caller-owned `record_opts`, `evlist`, `evsel`, and `perf_event_attr` structures. It reads sysctl state and may transiently open a perf event fd for capability probing. No persistent files are written.

## Dependencies and Integration Points

It integrates with evlist/evsel configuration, parse-events, perf syscall wrapper, perf API probes, topdown and memory event helpers, cpumaps, parse-options, and record option declarations in `record.h`.

## Risks and Edge Cases

Frequency parsing uses `atoi`, so malformed non-`max` strings become 0 and are rejected later only if configured. `evlist__can_select_event` uses the first requested or online CPU and may not represent all CPUs. Leader sampling rules are subtle for AUX/topdown/memory events and can accidentally suppress samples if config term detection misses a user override. Reading max sample rate failure is treated as nonfatal in config but fatal for `"max"` parsing.

## Test Signals

Tests should cover frequency vs period conflict, strict and non-strict max-rate behavior, zero defaults, `"max"` parsing, invalid strings, evlist sample-id decisions for homogeneous and heterogeneous sample types, AUX/topdown leader sampling, explicit config-term preservation, and selectability probing with mocked `perf_event_open` errors.
