# sources/distributed-fs/ceph-client/tools/net/ynl/pyproject.toml

Purpose: Defines Python packaging metadata for the `pyynl` package and console scripts.

Important configuration: Uses `setuptools.build_meta` with `setuptools>=61.0`. Project metadata names the package `pyynl`, version `0.0.1`, requires Python `>=3.9`, and depends on `pyyaml==6.*` and `jsonschema==4.*`. Package discovery includes `pyynl` and `pyynl.lib`. Console entry points expose `ynl = pyynl.cli:main` and `ynl-ethtool = pyynl.ethtool:main`.

Control flow: Build frontends read this file to build/install the package. The top-level Makefile invokes `pip install --prefix=... .`, which installs importable modules and script entry points.

Dependencies and integration: Ties the CLI and library to Python package tooling and the YNL Makefile install path. Runtime schema validation depends on the pinned major versions of PyYAML and jsonschema.

State and persistence: Produces build artifacts, package metadata, and installed scripts/modules when invoked by pip; no runtime state.

Risks: `ynl-ethtool` references `pyynl.ethtool`, which must exist in the package tree for installed entry points to work. Exact major-version dependency pins may conflict with system package policies. Package discovery omits deeper package names unless setuptools treats them as included through parent package discovery.

Test signals: `python -m build`, `pip install --prefix`, import `pyynl.lib`, run installed `ynl --help`, run `ynl-ethtool --help` if the module is present, and test with Python 3.9 plus newer supported interpreters.
