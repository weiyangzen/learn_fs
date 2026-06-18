# sources/distributed-fs/coda/coda-src/kerndep/pioctl.h

## Purpose
Public pioctl interface and ioctl-number helpers for Coda userland tools.

## APIs, Types, and Functions
Declares `pioctl()`, defines `PIOCTL_PREFIX`, `_VICEIOCTL(id)`, `_VALIDVICEIOCTL(com)`, and fallback `_IOC_*` decoding macros for Darwin, Cygwin, NetBSD, and FreeBSD. Includes `coda.h` for `ViceIoctl`.

## Control Flow, State, and Persistence
No runtime flow. The macros encode/decode command numbers and validate the 0-255 Coda pioctl id range.

## Dependencies and Integration
Included by tools that call Venus pioctls, especially repair utilities. Bridges system ioctl macro differences across supported platforms.

## Risks and Test Signals
Risks include platform macro drift, `_VALIDVICEIOCTL` range comparison on encoded command values, and warning that requests must fit Coda max message sizes. Test signals are correct `_VICEIOCTL(_VIOC_*)` values and cross-platform compilation.
