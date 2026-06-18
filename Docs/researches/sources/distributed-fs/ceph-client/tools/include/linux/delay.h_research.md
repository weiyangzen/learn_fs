# sources/distributed-fs/ceph-client/tools/include/linux/delay.h

## Purpose

This is a placeholder for kernel delay helpers in tools builds.

## APIs, State, and Dependencies

The file only contains an include guard and provides no delay functions or macros.

## Risks and Test Signals

Copied code that calls `udelay`, `mdelay`, or related helpers will not be satisfied by this header. Compile coverage is the validation signal.
