# sources/cloud-native/stargz-snapshotter/script/benchmark/tools/util.sh

Purpose: Shared percentile/sample helpers for benchmark post-processing.
Important APIs/types/functions: global `PERCENTILE`, `CALCTEMP`; functions `samples_num`, `min_samples`, and `percentile`.
Control flow: functions filter benchmark JSON with jq, compute sample counts, randomly select equal sample counts, sort values, and call Python/numpy percentile calculation.
State and persistence: creates one temp file for percentile inputs but never removes it in this script.
Dependencies and integration points: sourced by csv/plot/table/percentiles tools; requires jq and Python with numpy.
Risks: `min_samples` uses `IMGNAME` instead of its `IMAGE` parameter, coupling it to caller loop variable names. Numpy `interpolation` argument may warn or change under newer numpy versions.
Test signals: indirectly tested by every benchmark formatting path.
