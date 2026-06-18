# sources/compression/zlib/.github/workflows/fuzz.yml

Purpose: pull-request CI workflow that builds and runs zlib OSS-Fuzz fuzzers through CIFuzz.

Important APIs/actions: uses `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, `run_fuzzers@master`, and `actions/upload-artifact@v6`.

Control flow: on pull requests, builds fuzzers for OSS-Fuzz project `zlib`, runs them for 300 seconds, and uploads crash artifacts if any step fails.

State and persistence: CI-only `./out/artifacts` crash output retained as a workflow artifact on failure.

Dependencies and integration: depends on OSS-Fuzz infrastructure, zlib's external OSS-Fuzz project definition, and GitHub Actions Ubuntu runners.

Risks: actions are pinned to `master`, so upstream action changes can affect reproducibility. A 300-second fuzz window is a regression smoke test, not exhaustive fuzzing.

Test signals: detects sanitizer/fuzzer crashes triggered by current corpus and short exploratory fuzzing in pull requests.
