# sources/distributed-fs/ceph-client/samples/timers/Makefile

## Purpose

This Makefile builds the HPET user-space sample program.

## Important APIs, Types, and Functions

It sets `userprogs-always-y += hpet_example` and adds `userccflags += -I usr/include`.

## Control Flow

Kbuild compiles `hpet_example.c` as a user program when the timers samples are built.

## State and Persistence Behavior

Only build artifacts are affected.

## Dependencies and Integration Points

It integrates with UAPI headers for HPET ioctl constants.

## Risks and Edge Cases

The resulting binary needs an HPET device node and kernel HPET support at runtime.

## Test Signals

Build samples and verify `hpet_example` is produced.
