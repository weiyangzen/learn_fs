# sources/distributed-fs/ceph-client/tools/perf/builtin-buildid-list.c

Purpose: implements `perf buildid-list`, printing build IDs from an ELF file, a perf.data file, the running kernel, or current kernel/module maps.

Important APIs, types, and functions: `buildid__map_cb()` prints build IDs and address ranges for kernel maps. `buildid__show_kernel_maps()` constructs a host machine and iterates kernel maps. `sysfs__fprintf_build_id()` reads the running kernel build ID from sysfs. `filename__fprintf_build_id()` attempts direct ELF build-id extraction. `dso__skip_buildid()` filters by hit state. `perf_session__list_build_ids()` handles perf.data and pipe input, processing events as needed to mark hit DSOs. `cmd_buildid_list()` parses frontend options.

Control flow: command options select input, force, kernel-only, kernel maps, with-hits, and verbosity. Kernel modes bypass perf.data. Otherwise, the implementation first tries to treat the input as an ELF and print its build ID. If not, it opens a read-mode perf session with event callbacks that populate DSOs and mark hits, processes events when hits or pipe mode require it, and prints DSO build IDs.

State and persistence: no persistent state is written. It reads sysfs, ELF files, perf.data, and possibly compressed data through zstd session state. In pipe mode, build IDs are discovered by consuming the event stream.

Dependencies and integration points: uses perf session/data/header APIs, DSO and build-id helpers, symbol ELF initialization, machine kernel maps, pager support, and zstd initialization.

Risks: direct ELF detection means an ELF input short-circuits perf.data handling. AUXTRACE perf.data disables with-hit filtering because trace decoding is intentionally skipped. If zstd initialization fails, output may be incomplete but command continues with a warning. `with_hits` is forced when HEADER_BUILD_ID is absent. Kernel-map output depends on host symbol discovery.

Test signals: run against a known ELF, a perf.data with build-id header, perf.data without hits, pipe-mode data, `--kernel`, `--kernel-maps`, `--with-hits`, and compressed input. Validate force handling and warning behavior on damaged files.
