# sources/control-plane/mayastor/test/python/common/constants.py

## Purpose
Centralizes the Mayastor/OpenEBS NVMe NQN prefix used by tests.

## Important APIs, Types, And Functions
Defines `nvme_nqn_prefix = "nqn.2019-05.io.openebs"`.

## Control Flow
There is no control flow.

## State And Persistence
No state beyond the module constant.

## Dependencies And Integration Points
Imported by publish BDD tests and any code constructing expected NVMf subsystem names.

## Risks
If production NQN naming changes, tests using this constant can fail broadly or assert stale names.

## Test Signals
Consistent URI/NQN assertions across suites indicate naming compatibility.
