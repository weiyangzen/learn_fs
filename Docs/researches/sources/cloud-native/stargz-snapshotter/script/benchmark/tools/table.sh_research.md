# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/table.sh

Purpose: Renders benchmark JSON as a markdown table grouped by image.
Important APIs/types/functions: sources `util.sh`; env `TARGET_MODES`, `TARGET_IMAGES`.
Control flow: reads JSON from stdin, computes common sample count, prints a markdown report header, then emits pull/create/run percentile rows per mode for each image.
State and persistence: no persistent state beyond temporary JSON/stdin file.
Dependencies and integration points: depends on jq and Python/numpy through `util.sh`.
Risks: header text is hard-coded to a GitHub Actions Ubuntu runner; table separator is minimal markdown and assumes downstream renderer tolerance.
Test signals: used by `benchmark/test.sh` to create `result.md`.
