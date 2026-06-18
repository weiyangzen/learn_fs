# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops/hweight.h

## Purpose

This header is a small umbrella that brings together architecture and constant hweight implementations.

## APIs, State, and Dependencies

It includes `arch_hweight.h` and `const_hweight.h`, thereby exposing `hweight8`, `hweight16`, `hweight32`, `hweight64`, and constant-only variants through the generic bitops stack. It has no state or direct logic.

## Risks and Test Signals

The header relies on include order and linked software hweight functions. Tests are compile/link coverage for bitmap and bitops consumers that call hweight helpers.
