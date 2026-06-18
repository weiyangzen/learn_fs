# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/__init__.py

Purpose: Marks `pyynl` as a Python package.

Important APIs and state: The file is intentionally empty and exports no names. Public imports are provided through `pyynl.lib` and console entry points rather than the package root.

Control flow: Python package import machinery executes this file when `import pyynl` runs; because it is empty, it has no side effects.

Dependencies and integration: Used by setuptools package discovery and by installed console scripts that import modules under `pyynl`.

State and persistence: No runtime state and no persistence.

Risks: Root-level `import pyynl` provides no convenience exports, so users must import from `pyynl.lib` or submodules. This is low risk but should be intentional for API stability.

Test signals: Package discovery includes `pyynl`, `import pyynl` succeeds from an installed wheel or prefix install, and import has no side effects.
