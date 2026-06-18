# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/portability.h

Purpose: compatibility shim for pre-Leopard SDKs that may not define `NSInteger` and `NSUInteger`.

Important APIs and state: when `NSINTEGER_DEFINED` is absent, defines `NSInteger` and `NSUInteger` as long/unsigned long for 64-like builds or int/unsigned int otherwise, then defines min/max constants and marks `NSINTEGER_DEFINED`.

Control flow and persistence: header-only compile-time compatibility, no runtime state.

Dependencies and integration: included by `PListManager.m` and potentially other legacy Objective-C sources.

Risks: typedefs can conflict if included after newer Foundation headers with different definitions. Uses `LONG_MAX`, `LONG_MIN`, and `ULONG_MAX` without including limits here, relying on transitive includes.

Test signals: compile on old and new SDKs, 32-bit and 64-bit targets, include order with Cocoa/Foundation, and warnings about duplicate typedefs.
