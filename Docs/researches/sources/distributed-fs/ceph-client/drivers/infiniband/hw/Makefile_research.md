<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile

## Purpose
This Kbuild file selects hardware-provider subdirectories under `drivers/infiniband/hw` according to enabled kernel configuration symbols.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_INFINIBAND_MTHCA) += mthca/` and similar lines map each RDMA provider config option to its subdirectory.
- `obj-$(CONFIG_INFINIBAND_BNG_RE) += bng_re/` integrates the Broadcom next-generation RoCE driver into the hardware-provider build.

## Control Flow
Kbuild evaluates each `obj-*` expression during kernel or module build. If a config symbol is `y`, the subdirectory is built into the kernel; if it is `m`, the subdirectory contributes module objects; if unset, the directory is skipped.

## State And Persistence
The file does not persist runtime state. Its persistent effect is build graph shape: enabled drivers produce built-in objects or modules and disabled drivers are omitted.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system and the nested Makefiles in each provider directory, including `bng_re/Makefile`. It depends on the config symbols exported by provider Kconfig files and top-level RDMA build inclusion.

## Risks And Edge Cases
A wrong symbol or subdirectory name silently prevents a provider from building when configured. The `bng_re` entry must stay synchronized with `hw/bng_re/Kconfig` and the actual directory name. Ordering normally has limited semantic meaning, but duplicate or stale entries can create confusing build output.

## Test Signals
Build with `CONFIG_INFINIBAND_BNG_RE=y` and `=m` to confirm the `bng_re` directory is entered. A full RDMA hardware-provider build should show no missing-directory or unknown-symbol Kbuild errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/Makefile -->
