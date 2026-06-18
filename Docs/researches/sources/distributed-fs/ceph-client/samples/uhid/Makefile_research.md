# sources/distributed-fs/ceph-client/samples/uhid/Makefile

## Purpose

This Makefile builds the UHID user-space example program.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += uhid-example` and includes UAPI headers with `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles `uhid-example.c` as a user program.

## State and Persistence Behavior

Only build artifacts are produced.

## Dependencies and Integration Points

The sample uses `/dev/uhid` and Linux UHID UAPI headers.

## Risks and Edge Cases

Runtime requires UHID support and usually root or device permissions.

## Test Signals

Build samples and verify `uhid-example` is produced.
