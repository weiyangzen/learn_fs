# sources/cloud-native/soci-snapshotter/.github/workflows/benchmark-visualization.yml

Purpose: runs performance benchmarks, converts results to visualization data, and publishes benchmark history to GitHub Pages on main pushes.

Important APIs/types/functions: jobs `benchmark`, `download-and-convert-benchmark-result-to-visualization-data`, and `push-benchmark-result-gh-pages`; uses `make benchmarks-perf-test`, artifact upload/download, `scripts/visualization-data-converter.sh`, jq matrix generation, and `benchmark-action/github-action-benchmark`.

Control flow: push and selected PR changes build the project, run benchmark binaries, upload raw `results.json`, convert it into per-file JSON visualization data, then on push iterates those files to publish custom smaller-is-better benchmark data.

State and persistence: creates GitHub artifacts and updates gh-pages benchmark data on push.

Dependencies/integration: depends on Go setup, Makefile benchmark targets, converter script, jq, and GitHub token write/deployment permissions.

Risks: benchmarks run on shared GitHub runners and can be noisy. Matrix file paths are absolute workspace paths from conversion job but reused after artifact download, so path assumptions should be watched.

Test signals: PR workflow validates benchmark run/conversion without publishing; main push validates gh-pages publication.
