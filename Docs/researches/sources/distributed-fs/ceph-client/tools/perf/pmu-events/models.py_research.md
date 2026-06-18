<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py
Purpose: Maps CPU identifiers to PMU event model directory names by reading architecture `mapfile.csv` files. It is a small CLI helper for selecting model subsets used by PMU event generation.

Important APIs/types/functions: `main()` defines helpers `dir_path`, `find_archs`, `find_mapfiles`, and `find_cpuids`. `find_cpuids` converts `[[:xdigit:]]` regex syntax from mapfiles into Python-compatible `[0-9a-fA-F]` and returns model paths whose cpuid regex matches the requested cpuid list.

Control flow: The CLI accepts `arch`, `cpuid`, and `starting_dir`; chooses matching architecture directories; finds their `mapfile.csv`; scans non-comment rows; matches each requested cpuid against row 0; and prints comma-separated model names from row 2.

State and persistence: Stateless aside from local lists. It reads mapfiles and writes only stdout.

Dependencies and integration points: Depends on `argparse`, `csv`, `os`, and `re`. It integrates with the PMU events build process and can feed the `model` argument of `jevents.py`/`intel_metrics.py`.

Risks: The first-row skipping variable is named confusingly and must preserve mapfile header behavior. Matching is only as accurate as mapfile regexes, and the script supports comma-separated cpuid input without trimming spaces.

Test signals: Run against known architecture mapfiles and cpuid strings; compare model output to expected mapfile row selections and confirm `arch=all` scans all architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/models.py -->
