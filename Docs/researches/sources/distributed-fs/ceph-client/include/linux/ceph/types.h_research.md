# sources/distributed-fs/ceph-client/include/linux/ceph/types.h

## Purpose

`types.h` is a small umbrella for core Ceph kernel types that must be available before including `ceph_fs.h`.

## Important APIs, Types, and Functions

It includes foundational kernel and Ceph headers, then defines `struct ceph_vino` with inode and snapshot id, and `struct ceph_cap_reservation` with reserved and used capability counts.

## Control Flow

There is no runtime flow. The types are embedded in higher-level CephFS inode/capability code.

## State and Persistence Behavior

`ceph_vino` identifies a Ceph inode version in a snapshot context; it is value state copied through lookup and inode paths. `ceph_cap_reservation` tracks transient reservation accounting.

## Dependencies and Integration Points

It includes Linux networking/types/fcntl/string plus `ceph_fs.h`, `ceph_frag.h`, and `ceph_hash.h`. It is a common include for libceph and CephFS source files.

## Risks and Edge Cases

Include ordering is the main concern because the file exists partly to break dependency cycles. Snapshot sentinel values come from `rados.h` via `ceph_fs.h` and must be interpreted consistently.

## Test Signals

Build coverage for include order, inode lookup tests involving snapshot ids, and capability reservation accounting tests.
