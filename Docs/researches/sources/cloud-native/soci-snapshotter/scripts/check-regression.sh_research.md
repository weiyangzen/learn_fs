# sources/cloud-native/soci-snapshotter/scripts/check-regression.sh

Purpose: compares benchmark JSON results and fails if current P90 timings regress beyond a threshold.

Important APIs/types/functions: `calculate_threshold` computes 110% of the past value. `calculate_p90_after_skip` sorts benchmark times after dropping the first sample. `compare_stat_p90` and `compare_p90_values` compare `fullRunStats`, `pullStats`, `lazyTaskStats`, and `localTaskStats` for each benchmark test.

Control flow: require two JSON paths, load JSON into variables, iterate test names from past JSON, compute past/current P90s for each stat, flag regressions, print success/failure, and exit accordingly.

State and persistence: read-only over input JSON files.

Dependencies/integration points: requires `jq`, `bc`, `awk`, `sort`, and benchmark JSON with `.benchmarkTests[].<stat>.BenchmarkTimes`.

Risks: comment says 150% but code uses 1.1 and error text says 110%. P90 index calculation uses original length despite skipping one sample, which may bias indexing. Missing current test/stat values can produce invalid numeric comparisons.

Test signals: serves as performance regression gate for benchmark result files.
