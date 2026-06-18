# sources/distributed-fs/coda/coda-src/kerndep/Makefile.am

## Purpose
Automake definition for the small kernel-dependency compatibility library.

## APIs, Types, and Functions
Builds `libkerndep.la` from `pioctl.c`, `pioctl.h`, and `coda.h`, with base include path.

## Control Flow, State, and Persistence
No runtime behavior. It packages userland Coda kernel-interface definitions and pioctl implementation for clients/tools.

## Dependencies and Integration
Linked by repair utilities and other code needing `pioctl()` or Coda kernel protocol structures.

## Risks and Test Signals
Risks are ABI drift against kernel/Venus expectations and generated config differences. Test signals are successful library build and pioctl consumers linking.
