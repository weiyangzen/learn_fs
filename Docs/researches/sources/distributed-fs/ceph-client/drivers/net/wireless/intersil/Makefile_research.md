# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/Makefile

## Purpose
This Makefile descends into the p54 subdirectory when p54 common support is selected.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_P54_COMMON) += p54/` attaches the p54 directory to kbuild.

## Control Flow
kbuild includes the p54 subdirectory only when `CONFIG_P54_COMMON` is enabled as built-in or module.

## State and Persistence Behavior
No runtime state is involved. Build output depends on `.config`.

## Dependencies and Integration Points
It integrates the vendor-level Intersil directory with the p54 Makefile.

## Risks and Edge Cases
If a future Intersil driver does not depend on `P54_COMMON`, this Makefile would need additional object rules. Current behavior matches the single sourced subdriver tree.

## Test Signals
Successful kernel build with `CONFIG_P54_COMMON=y/m` confirms traversal into `p54/`.
