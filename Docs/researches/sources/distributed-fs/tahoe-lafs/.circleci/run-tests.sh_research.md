## sources/distributed-fs/tahoe-lafs/.circleci/run-tests.sh

Purpose: executes tox test environments in CircleCI, captures subunit/JUnit artifacts, and supports allowed-failure jobs.

Important behavior: strict Bash mode; inputs bootstrap venv, project root, allowed-failure flag, artifact path, tox environment, and extra tox args. It configures subunit output paths, enforces a 45 minute timeout with 1 minute kill grace, exports trial args and unbuffered output, and runs tox with `/tmp/tahoe-lafs.tox` workdir.

Control flow: if artifacts are enabled, it requires the subunit file after tox and converts it to JUnit XML using the environment's `subunit2junitxml`. If `ALLOWED_FAILURE=yes`, failures are converted to success via `true`; otherwise they fail.

State and dependencies: writes artifacts, tox workdir, and possibly trial logs in the checkout. Depends on GNU timeout, tox, and subunit tooling.

Risks: `|| "${alternative}"` relies on `true`/`false` command strings; binary subunit handling is brittle but explicit. Timeout may kill very slow legitimate jobs.
