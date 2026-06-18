# sources/distributed-fs/ceph-client/include/linux/cgroup_api.h

## Purpose

`cgroup_api.h` is a compatibility shim that simply includes `linux/cgroup.h`.

## Important APIs, Types, and Functions

It declares no independent symbols. All visible API is inherited from `cgroup.h`.

## Control Flow

There is no control flow. Including this header is equivalent to including the main cgroup interface.

## State and Persistence Behavior

No state is owned here.

## Dependencies and Integration Points

Its only dependency and integration point is `linux/cgroup.h`. It likely preserves include compatibility for code that still includes `cgroup_api.h`.

## Risks and Edge Cases

The risk is include indirection: changes to `cgroup.h` affect all users, and removing this shim can break out-of-tree or older in-tree includes.

## Test Signals

Compile users that include `cgroup_api.h` directly, both with cgroups enabled and disabled.
