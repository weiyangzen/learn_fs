# sources/cloud-native/composefs-rs/examples/pyproject.toml

Purpose: pytest configuration for example VM tests.

Important APIs/types/functions: `[tool.pytest.ini_options]` with strict markers, verbose output, automatic asyncio mode, `pythonpath = "."`, and `testpaths = ["test"]`.

Control flow: pytest reads this when invoked from examples, enabling async tests without explicit decorators and discovering only the `test` directory.

State/persistence: repository configuration only.

Dependencies/integration: integrates with `pytest`, `pytest-asyncio`, `testthing.py`, and `examples/test/run`.

Risks/test signals: broad `pythonpath="."` relies on running from examples root. Misconfiguration prevents async VM tests from running.
