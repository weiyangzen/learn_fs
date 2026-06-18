# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/csv.sh

Purpose: Converts benchmark JSON rows into a compact CSV table by image, operation, and mode.
Important APIs/types/functions: sources `util.sh`; uses `min_samples` and `percentile`; env `TARGET_MODES`, `TARGET_IMAGES`.
Control flow: reads JSON from stdin into a temp file, determines modes/images, computes the common minimum sample count across mode/image combinations, then emits pull/create/run rows with percentile values.
State and persistence: stores stdin in a temp file and uses `util.sh`'s shared percentile temp file.
Dependencies and integration points: depends on `jq`, Python/numpy through `util.sh`, and well-formed benchmark JSON.
Risks: `min_samples` in `util.sh` references global `IMGNAME`, so callers must preserve that variable name; empty sample sets can break numpy percentile.
Test signals: indirectly exercised by `benchmark/test.sh` formatting stage.
