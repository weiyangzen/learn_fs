<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml


## Purpose
GitHub Actions CodeQL workflow for Go security/static analysis.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch, pushes to master, pull requests to master excluding markdown-only changes, and a weekly Tuesday cron. It grants contents read and security-events write permissions, uses concurrency cancellation, checkout, setup-go, CodeQL init/autobuild/analyze.


## Control Flow
Runs only in ipfs/kubo unless manually dispatched. CodeQL analyzes Go and uploads security events.


## State and Persistence Behavior
State is CodeQL analysis results and GitHub code scanning alerts. No repository writes.


## Dependencies and Integration Points
Depends on actions/checkout@v6, actions/setup-go@v6, github/codeql-action v4, go.mod toolchain metadata, and GitHub code scanning permissions.


## Risks and Test Signals
Risks include 20-minute timeout and autobuild assumptions. Signal provides scheduled and PR security analysis for Go code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/codeql-analysis.yml -->
