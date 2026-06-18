<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/tox.ini -->
## sources/control-plane/longhorn-engine/integration/tox.ini

Purpose: tox configuration for Python integration tests and flake8.

Important APIs/types/functions: `[tox]` defines `envlist=flake8, py3`. default testenv installs `requirements.txt`, changes to tox root, runs `py.test core data instance --durations=20 {posargs} --exitfirst`, and passes backup-related environment variables. `testenv:flake8` installs flake8 requirements and checks `core data instance`, with generated RPC files excluded.

Control flow and state: tox creates virtualenvs and runs pytest/flake8; no application state.

Dependencies and integration points: integrates with integration test suites under `core`, `data`, and `instance`; relies on AWS/BACKUPTARGET environment variables for backup tests.

Risks: generated RPC exclusion list does not include SPDK generated files, so stale/generated formatting might be noisy if included elsewhere. `py.test` command naming and distutils-era packaging may be sensitive to newer Python environments. `--exitfirst` improves feedback but hides later failures in full validation.

Test signals: this is itself the test runner entrypoint for the integration directory.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/integration/tox.ini -->
