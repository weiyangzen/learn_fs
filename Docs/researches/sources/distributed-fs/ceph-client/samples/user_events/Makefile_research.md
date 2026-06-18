# sources/distributed-fs/ceph-client/samples/user_events/Makefile

## Purpose

This Makefile builds the user_events sample program with direct compile rules.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wl,-no-as-needed -Wall -I../../usr/include`, declares `example: example.o`, and `example.o: example.c`.

## Control Flow

Unlike Kbuild `userprogs` fragments, this is a simple make rule for compiling and linking `example`.

## State and Persistence Behavior

Only the built executable/object are affected.

## Dependencies and Integration Points

It depends on user_events UAPI headers and linker behavior retaining needed libraries/objects.

## Risks and Edge Cases

The include path is relative and assumes invocation from this directory. It does not define a clean target.

## Test Signals

Run `make` in the directory and verify `example` builds.
