# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/percentiles.sh

Purpose: Creates per-image percentile CSV/data/gnuplot outputs for benchmark timings.
Important APIs/types/functions: sources `util.sh`; defines gnuplot `template`; env `TARGET_MODES`, `TARGET_IMAGES`, `BENCHMARK_PERCENTILES_GRANULARITY`.
Control flow: reads JSON from stdin, chooses modes/images and common sample count, writes raw data, plot files, PNG graphs, and CSV files for pull/create/run percentiles across a configured granularity.
State and persistence: creates `raw`, `plt`, `png`, and `csv` subdirectories under the output directory.
Dependencies and integration points: depends on jq, Python/numpy, gnuplot, and benchmark JSON fields.
Risks: uses `mkdir` without `-p`; rerunning into an existing directory with those subdirs fails. Random sample selection in `percentile` means outputs can vary.
Test signals: run by `benchmark/test.sh` after successful benchmark execution.
