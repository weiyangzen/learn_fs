## sources/distributed-fs/tahoe-lafs/.circleci/rebuild-images.sh

Purpose: convenience script to trigger the CircleCI image-building workflow through the CircleCI API v2.

Important behavior: strict Bash mode, expects API token and branch arguments, then POSTs to the Tahoe-LAFS project pipeline endpoint with parameters `{build-images: true, run-tests: false}`.

Control flow: shifts positional arguments and invokes `curl --verbose` with token and JSON payload.

State and dependencies: does not modify local files; creates a remote CircleCI pipeline. Depends on a valid user API token, network access, and CircleCI project permissions.

Risks: token is passed on the command line where local process listings or shell history may expose it. The script intentionally suppresses normal tests for image rebuilds, so image changes need separate validation.
