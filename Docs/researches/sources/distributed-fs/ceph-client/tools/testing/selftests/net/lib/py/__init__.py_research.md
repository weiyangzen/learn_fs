# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/__init__.py

## Purpose
This package initializer presents a single import surface for Python networking selftests.

## Important APIs and Types
It re-exports constants, KTAP helpers, assertions, namespace classes, netdevsim classes, command wrappers, BPF map helpers, and YNL family wrappers through `__all__`. Key exports include `ksft_run`, `ksft_exit`, `NetNS`, `NetNSEnter`, `cmd`, `bkg`, `defer`, `bpftool`, `ip`, `NetdevSimDev`, `YnlFamily`, `RtnlFamily`, `EthtoolFamily`, `NetdevFamily`, and `Netlink`.

## Control Flow and State
Importing this module imports the submodules and exposes their names. It has no independent runtime control flow or state beyond Python import caching.

## Dependencies and Integration
It depends on sibling modules in `lib/py`. Tests can write `from lib.py import ...` without knowing the internal module layout.

## Risks and Test Signals
Import failures in any re-exported module can prevent all users from starting. The `__all__` list is the integration contract; omissions there affect wildcard imports and public package clarity.
