# sources/distributed-fs/ceph-client/tools/include/asm/io.h

## Purpose

This header selects the architecture MMIO accessor implementation for tools builds.

## APIs, State, and Dependencies

It includes the x86 tools `asm/io.h` on i386/x86_64 and generic MMIO accessors otherwise. It defines no direct functions and has no state.

## Risks and Test Signals

Relative architecture include paths and generic fallback semantics are the key risks. Tests should compile users on x86 and non-x86 configurations and verify any MMIO-dependent tool has the required ordering semantics.
