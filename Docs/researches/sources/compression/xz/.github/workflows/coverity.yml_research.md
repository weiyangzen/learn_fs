# sources/compression/xz/.github/workflows/coverity.yml

## Purpose
This workflow submits Coverity Scan analysis for the special `coverity_scan` branch. It builds an autotools debug configuration and hands the build command to a pinned Coverity action.

## Important Control Flow
The job checks out the repo, installs autotools and multilib dependencies, runs `./autogen.sh --no-po4a`, configures with `--enable-debug --disable-silent-rules`, appends `#define LZMA_RANGE_DECODER_CONFIG 0` to `config.h` to avoid known inline-assembly false positives, and invokes `vapier/coverity-scan-action`.

## State, Dependencies, and Integration
It depends on Ubuntu packages, repository secrets for Coverity email/token, generated autotools files, and Coverity's build capture. State includes generated configure outputs and modified `config.h` within the ephemeral runner.

## Risks and Test Signals
The workflow provides static-analysis coverage, not runtime validation. It is branch-gated and secret-dependent, so it will not run for ordinary PRs. The explicit inline assembly disablement trades analysis precision for fewer false positives.
