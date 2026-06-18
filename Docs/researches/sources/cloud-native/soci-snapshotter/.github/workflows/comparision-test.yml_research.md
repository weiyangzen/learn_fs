# sources/cloud-native/soci-snapshotter/.github/workflows/comparision-test.yml

Purpose: scheduled/PR workflow for comparison benchmarks between SOCI and overlayfs.

Important APIs/types/functions: Go setup, `make`, `make benchmarks`, and `cat benchmark/comparisonTest/output/results.json`.

Control flow: runs every two days and on benchmark/Makefile/workflow PR changes. It builds the project, runs benchmark suite, and prints comparison results.

State and persistence: writes benchmark output under `benchmark/comparisonTest/output` in CI workspace.

Dependencies/integration: depends on Makefile benchmark targets and benchmark harness.

Risks: filename is misspelled `comparision-test.yml`, while PR path filter references `.github/workflows/comparison-test.yml`; changes to this workflow itself may not trigger the PR workflow. Benchmarks require sudo and stable host behavior.

Test signals: scheduled runs and benchmark output JSON.
