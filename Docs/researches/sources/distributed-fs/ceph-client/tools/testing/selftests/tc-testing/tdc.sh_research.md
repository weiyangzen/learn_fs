# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc.sh

## Purpose
Shell wrapper that attempts to load traffic-control action, classifier, ematch, and qdisc modules before running `./tdc.py` in parallel with `-J$(nproc)`.

## Important APIs, Types, and Functions
Defines `try_modprobe()`, which checks `modprobe -q -R` for module availability before calling `modprobe`. The module list includes netdevsim, many `act_*`, `cls_*`, `em_*`, and `sch_*` modules such as `sch_htb`, `sch_teql`, and `sch_dualpi2`.

## Control Flow
The script sequentially calls `try_modprobe` for each module. Missing modules print a skip-style message but do not abort. After loading attempts, it executes `tdc.py` with worker count equal to `nproc`.

## State and Persistence Behavior
It changes kernel module load state. It does not persist files directly, but `tdc.py` may create result outputs and manipulate namespaces/devices.

## Dependencies and Integration Points
Depends on `/bin/sh`, `modprobe`, module alias resolution, `nproc`, and the local `tdc.py`. It integrates with kselftest execution as the convenient top-level TDC runner.

## Risks and Edge Cases
The script does not stop if a required module is missing; failures surface later as individual TDC failures. It assumes it runs from the tc-testing directory. Loading many modules can require privileges and may be inappropriate on minimal systems.

## Test Signals
Signals include module load messages, successful startup of `tdc.py`, and TDC test output showing which cases passed or failed after module preparation.
