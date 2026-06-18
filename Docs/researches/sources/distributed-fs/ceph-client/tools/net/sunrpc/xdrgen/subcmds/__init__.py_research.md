# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/__init__.py

Purpose: Marks the `subcmds` directory as a Python package for documentation tooling.

Important APIs and functions: No runtime subcommand registry is defined here.

Control flow: None.

State and persistence behavior: No state.

Dependencies and integration points: Helps sphinx-apidoc/package discovery for `declarations`, `definitions`, `lint`, and `source` modules.

Risks: None directly; actual command dispatch must be implemented elsewhere.

Test signals: Import `subcmds` and verify documentation tools include the package.
