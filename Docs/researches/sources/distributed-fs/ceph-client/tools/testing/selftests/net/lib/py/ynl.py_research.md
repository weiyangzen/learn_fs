# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/ynl.py

## Purpose
This module bridges network selftests to the kernel YNL Python library and pre-binds common netlink family specs.

## Important APIs and Types
It imports and re-exports `YnlFamily`, `NlError`, `NlPolicy`, and `Netlink`. Wrapper classes `EthtoolFamily`, `RtnlFamily`, `RtnlAddrFamily`, `NetdevFamily`, `NetshaperFamily`, `NlctrlFamily`, `DevlinkFamily`, and `PSPFamily` call `YnlFamily` with the matching YAML spec and disabled schema validation for speed.

## Control Flow and State
At import time it decides between installed selftests and in-tree source layout by checking for `kselftest-list.txt`. It appends the chosen tools path to `sys.path`, imports the YNL library, sets `SPEC_PATH`, or emits a KTAP skip and exits with code 4 if import fails. Wrapper instantiation opens family access based on YAML specs.

## Dependencies and Integration
It depends on `consts.py`, `ksft.py`, kernel `tools/net/ynl` Python modules, and YAML specs under either installed `net/lib/specs` or in-tree `Documentation/netlink/specs`. `link_netns.py` uses `RtnlFamily` for notification checking.

## Risks and Test Signals
Import-time exit means missing YNL support skips the whole test process. The path heuristic assumes either installed selftests or kernel source layout. Successful operation is indicated by wrapper construction and valid YNL request/notification behavior.
