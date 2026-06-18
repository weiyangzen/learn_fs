# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/consts.py

## Purpose
This module centralizes path constants and the current test program name for Python network selftests.

## Important APIs and Values
`KSFT_DIR` resolves to the selftests tree rooted above `lib/py`. `KSRC` resolves to the kernel source root. `KSFT_MAIN_NAME` is the current script basename without suffix, used in KTAP result names.

## Control Flow and State
The module performs path resolution at import time using `Path(__file__)` and `sys.argv[0]`. There is no mutable state.

## Dependencies and Integration
It is consumed by `ksft.py` for KTAP naming and by `ynl.py` to choose in-tree versus installed YNL/spec paths.

## Risks and Test Signals
The relative path calculation assumes the kernel selftest directory layout. Running scripts from unusual wrappers can alter `sys.argv[0]` and therefore KTAP case names.
