## sources/distributed-fs/tahoe-lafs/integration/__init__.py

Purpose: package marker for Tahoe-LAFS integration tests.

Important APIs: none; the file is empty.

Control flow: none.

State and dependencies: no persistence and no imports. Its role is to make `integration` importable by tests, benchmarks, and helper modules such as `benchmarks/conftest.py`.

Risks and signals: because it has no behavior, risk is limited to package discovery. Changes here would only matter if import side effects or package metadata were introduced later.
