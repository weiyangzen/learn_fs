<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/smack.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/smack.h

## Purpose
This header defines the Smack-specific security property payload used by the generic LSM property container.

## Important APIs, Types, and Functions
It forward-declares `struct smack_known` and defines `struct lsm_prop_smack` with a pointer to a Smack label object.

## Control Flow
There is no executable flow. Smack property producers store a label pointer, and generic LSM property consumers can carry it alongside other LSM metadata.

## State and Persistence Behavior
The header stores no independent state. The pointer references runtime Smack label state managed by Smack.

## Dependencies and Integration Points
It integrates with Smack and generic LSM property stacking code.

## Risks and Test Signals
Risks include stale label pointers, missing initialization, and stacking conversion mistakes. Test signals are Smack access tests, audit label output, and multi-LSM property tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/smack.h -->
