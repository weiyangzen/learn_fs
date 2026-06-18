# sources/compression/zstd/.github/workflows/nightly.yml

Purpose: scheduled and branch-triggered nightly regression workflow.

Important behavior: runs daily at midnight UTC and on pushes to `release`, `dev`, and branches matching `*nightly*`. The active job checks out code, installs `libcurl4-openssl-dev`, builds `programs/zstd`, and builds/runs `tests/regression`. A block of longer historical tests is left commented as documentation for possible nightly expansion.

State, dependencies, and integration: state is only apt packages and build outputs. It integrates the program build and regression harness, but does not upload comparison artifacts in this workflow.

Risks and test signals: as written it is much narrower than the long/short PR workflows and may duplicate only part of commit regression coverage. It is still useful as a scheduled signal for drift in runner images, package dependencies, and regression test health between active development events.
