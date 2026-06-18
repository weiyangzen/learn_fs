# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/plot.sh

Purpose: Generates a stacked histogram PNG comparing pull/create/run time per image and mode.
Important APIs/types/functions: sources `util.sh`; writes `result.plt`, `result.png`, and per-image `.dat` files.
Control flow: reads JSON, computes common sample count, writes a gnuplot script with one histogram per image, writes data rows for each mode, and invokes gnuplot.
State and persistence: persists plot/data files in the specified output directory.
Dependencies and integration points: depends on jq, Python/numpy, and gnuplot.
Risks: image names are sanitized only for `/` and `:`, and gnuplot labels may still be awkward; percentile randomness can make plots non-reproducible.
Test signals: called by `benchmark/test.sh` formatting stage.
