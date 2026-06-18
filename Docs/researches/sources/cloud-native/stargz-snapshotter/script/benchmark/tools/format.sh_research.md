# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/format.sh

Purpose: Extracts the JSON benchmark payload from noisy run logs.
Important APIs/types/functions: constant `OUTPUT_MARK=BENCHMARK_OUTPUT:` plus a grep/sed pipeline.
Control flow: filters stdin for marked lines, strips the prefix, and repairs trailing comma/newline combinations to produce a JSON array.
State and persistence: no persistent state.
Dependencies and integration points: consumed by `benchmark/test.sh` before plot/table/CSV generation.
Risks: fragile to changed output marker or JSON formatting; grep exits nonzero if no rows exist under `set -e`.
Test signals: validated when downstream `jq`-based tools accept the formatted JSON.
