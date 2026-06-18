# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/__init__.py

Purpose: Marks the `xdrgen` directory as a Python package for documentation tooling.

Important APIs and functions: No runtime APIs are defined; the file contains only SPDX and a note for `sphinx-apidoc`.

Control flow: None.

State and persistence behavior: No state.

Dependencies and integration points: Allows package discovery/import documentation for sibling modules such as `xdr_ast`, `xdr_parse`, `generators`, and `subcmds`.

Risks: None functionally, though package import behavior may depend on how the tool is executed because the generator modules use top-level imports.

Test signals: Import `xdrgen` or run sphinx-apidoc over the directory and verify package discovery.
