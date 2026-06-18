# sources/cloud-native/soci-snapshotter/scripts/visualization-data-converter.sh

Purpose: converts benchmark result JSON into per-test JSON metric files for visualization.

Important APIs/types/functions: `create_json_file` writes an array with lazy, local, and pull task duration P90 metrics. The main loop reads `.benchmarkTests[$i].testName`, `.lazyTaskStats.pct90`, `.localTaskStats.pct90`, and `.pullStats.pct90`.

Control flow: require input file and output directory args, check input exists, count benchmark tests with jq, iterate indices, extract fields, and write `<output_dir>/<testName>.json`.

State and persistence: writes one JSON file per benchmark test into the output directory.

Dependencies/integration points: requires `jq` and an existing output directory. Output format appears intended for dashboard/visualization ingestion.

Risks: does not create `output_dir`; test names with path separators or unsafe characters will affect output paths. JSON is hand-built with shell interpolation and can break if test names contain quotes or special characters.

Test signals: no direct tests; consumer visualization or JSON parsing would reveal malformed output.
