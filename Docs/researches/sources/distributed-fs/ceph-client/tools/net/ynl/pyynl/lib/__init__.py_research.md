# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/lib/__init__.py

Purpose: Public Python library aggregator for YNL spec parsing, runtime netlink access, and documentation generation.

Important APIs and state: Re-exports `SpecAttr`, `SpecAttrSet`, `SpecEnumEntry`, `SpecEnumSet`, `SpecFamily`, `SpecOperation`, `SpecSubMessage`, `SpecSubMessageFormat`, `SpecException`, `YnlFamily`, `Netlink`, `NlError`, `NlPolicy`, `YnlException`, and `YnlDocGenerator`. `__all__` explicitly defines the supported import surface.

Control flow: Importing `pyynl.lib` imports the spec parser, runtime implementation, and doc generator modules, then binds their selected symbols into the package namespace.

Dependencies and integration: Used by `pyynl/cli.py`, likely by generators and external Python consumers that want a stable `from pyynl.lib import ...` entry point.

State and persistence: No direct runtime state. Importing this package may load dependencies such as `yaml`, `socket`, and runtime classes from child modules.

Risks: Because imports are eager, consumers needing only spec parsing still import runtime/socket-related code and doc generator dependencies. Changes to `__all__` are user-visible API changes.

Test signals: `from pyynl.lib import *`, direct import of each listed symbol, package import from installed environment, and static checks that `__all__` matches available names.
