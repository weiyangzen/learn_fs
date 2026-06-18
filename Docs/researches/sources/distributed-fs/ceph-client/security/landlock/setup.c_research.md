# sources/distributed-fs/ceph-client/security/landlock/setup.c

## Purpose

`setup.c` registers Landlock as an LSM, declares its blob sizes, computes runtime errata bits, initializes ID generation, registers hooks, and marks the subsystem initialized.

## Important APIs, Types, and Functions

`landlock_initialized` gates cleanup paths before full init. `landlock_lsmid` names and IDs the LSM. `landlock_blob_sizes` declares credential, file, inode, and superblock blob sizes. `landlock_errata` stores runtime errata bits. `compute_errata()` consumes `landlock_errata_init[]`. `landlock_init()` registers credential, task, filesystem, and network hooks, initializes IDs, and sets initialized state. `DEFINE_LSM(LANDLOCK_NAME)` binds the init function and blob sizes to the LSM framework.

## Control Flow

At LSM initialization, `compute_errata()` validates errata ABI entries and sets the bitmask. Hook registration functions are called in sequence. Audit ID state is initialized through real or stub `landlock_init_id()`. The subsystem is then marked initialized and logs readiness.

## State and Persistence Behavior

Blob sizes become part of LSM-managed object allocation. `landlock_errata` and `landlock_initialized` are `__ro_after_init`. Runtime domains and rules are created later by syscalls.

## Dependencies and Integration Points

The file depends on LSM infrastructure, UAPI LSM ID, Landlock headers for every hook area, errata table, and optional stubs for networking/audit.

## Risks and Test Signals

Blob-size mismatches corrupt credentials/files/inodes/superblocks. Hook registration order should remain consistent with dependencies. Test boot with Landlock enabled in `CONFIG_LSM`, errata bit reporting, audit and non-audit builds, and early unmount paths before initialization.
