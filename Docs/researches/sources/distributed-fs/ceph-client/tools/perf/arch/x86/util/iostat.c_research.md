# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/iostat.c

Purpose: implements x86 perf stat `--iostat` support for Intel uncore IIO root-port bandwidth metrics. It discovers root ports from sysfs, optionally filters them, generates uncore event groups, and formats metric rows by root port.

Important APIs/types/functions: `struct iio_root_port` stores PCI domain, bus, die, PMU index, and list index. `struct iio_root_ports_list` owns discovered ports. `iostat_parse()` scans and filters root ports and sets `config->iostat_run`. `iostat_prepare()` replaces unsupported user events with generated IIO event groups. `iostat_print_metric()` converts raw event counts into MB-like values. `iostat_print_counters()`, `iostat_prefix()`, `iostat_list()`, and `iostat_release()` handle output and cleanup.

Control flow: `iio_pmu_count()` counts `uncore_iio_N` PMUs. `iio_mapping()` reads per-die mapping files such as `uncore_iio_%d/die%d` and builds root-port objects. Optional filter parsing accepts comma-separated `domain:bus` tokens. `iostat_event_group()` builds four events per root port for inbound/outbound read/write, parses them into the evlist, and attaches root-port pointers to each evsel. Printing walks selected counters, emits a new prefix when the root port changes, and scales counts by enabled/running ratio.

State and persistence: global `root_ports` is built during option parsing and consumed by prepare. Ownership transfers to evsel `priv` pointers; `iostat_release()` frees unique root-port objects. No persistent files are written; state comes from live sysfs and perf counter values.

Dependencies and integration: depends on perf stat config/output APIs, sysfs mountpoint and `sysfs__read_str()`, parse-events, evlist/evsel, perf counts, CPU/node topology, regex parsing, and Intel uncore IIO PMU naming. It integrates as an x86-specific perf stat mode.

Risks: this is platform-specific and fails on missing/changed IIO sysfs layout. `iostat_prepare()` assigns a new local evlist after `evlist__delete()` without returning it, so callers must already match this expected perf stat flow. Filtering transfers pointers by nulling old list entries; release logic depends on grouped evsel order and unique pointer changes. JSON prefix formatting is explicitly marked incorrect.

Test signals: `perf stat --iostat=list`, filtered `--iostat=0000:3d`, unsupported systems, interval/csv output, repeated runs under leak checking, and validation that four events per root port appear with expected metric labels.
