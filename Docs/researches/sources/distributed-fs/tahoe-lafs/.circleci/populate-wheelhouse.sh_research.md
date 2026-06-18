## sources/distributed-fs/tahoe-lafs/.circleci/populate-wheelhouse.sh

Purpose: builds or downloads wheels for Tahoe-LAFS test dependencies into a shared CI wheelhouse.

Important behavior: strict Bash mode, inputs wheelhouse path, bootstrap virtualenv, and project root, exports `PIP_FIND_LINKS` to the local wheelhouse, and runs `pip wheel --wheel-dir` for project extras `[testenv]` and `[test]`.

Control flow: uses the bootstrap virtualenv pip and forces `LANG=en_US.UTF-8` for the wheel operation because some dependencies historically require UTF-8 when building.

State and dependencies: writes wheel files to the wheelhouse and reads package metadata from the project root. Depends on pip, build tooling installed in the bootstrap venv, and package indexes unless all wheels are already available.

Risks: wheelhouse contents are platform/Python specific, so cache keys must match environment. Build failures surface during image preparation rather than test execution.
