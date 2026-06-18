# sources/distributed-fs/glusterfs/xlators/features/quota/src/Makefile.am

## Purpose

This Automake file builds the server-side quota and quotad translator modules when server support is enabled.

## Important APIs, Types, and Functions

Under `if WITH_SERVER`, it defines `xlator_LTLIBRARIES = quota.la quotad.la`. It sets module flags for both libraries, source lists for `quota_la_SOURCES = quota.c quota-enforcer-client.c` and `quotad_la_SOURCES = quotad.c quotad-helpers.c quotad-aggregator.c`, library dependencies on libglusterfs, XDR, and RPC libraries, quota headers, include paths, and warning flags.

## Control Flow

Configure-time `WITH_SERVER` controls whether quota modules are built. When enabled, the build compiles quota enforcement/client support and quotad helper/aggregator code and links the two xlator modules.

## State and Persistence Behavior

The makefile does not define runtime state. It determines which quota binaries are produced and installed.

## Dependencies and Integration Points

Quota links against libglusterfs, `libgfxdr`, and `libgfrpc`, includes RPC headers and DHT headers, and installs into the standard Gluster xlator feature directory.

## Risks and Edge Cases

Client-only builds will not produce these modules because of `WITH_SERVER`. Source/header lists must stay synchronized with quota implementation files; missing RPC or DHT include paths break compile. Marker's quota integration depends on these quota components at runtime even though marker has its own helper code.

## Test Signals

Build with `WITH_SERVER` enabled and disabled, verify both `quota.la` and `quotad.la` link when enabled, and run clean builds to catch source/header dependency drift.
