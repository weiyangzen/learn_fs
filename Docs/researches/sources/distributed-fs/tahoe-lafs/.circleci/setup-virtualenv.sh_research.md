## sources/distributed-fs/tahoe-lafs/.circleci/setup-virtualenv.sh

Purpose: pre-installs dependencies for a tox environment without running tests.

Important behavior: strict Bash mode; inputs bootstrap venv, project root, wheelhouse path, tox environment, and extra tox args. It invokes bootstrap `tox` against the project `tox.ini` with `--workdir /tmp/tahoe-lafs.tox --notest`.

Control flow: argument shifts collect optional tox args, then a single tox command creates or refreshes the target environment.

State and dependencies: writes tox environment state under `/tmp/tahoe-lafs.tox`; reads project configuration. Wheelhouse-related pip flags are commented out, so actual behavior depends on surrounding environment such as `PIP_FIND_LINKS`.

Risks: commented `PIP_NO_INDEX` means jobs can reach PyPI unless environment overrides. Failure here prevents tests from starting, but catches dependency issues early.
