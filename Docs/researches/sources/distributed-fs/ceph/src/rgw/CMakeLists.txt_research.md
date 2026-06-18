# sources/distributed-fs/ceph/src/rgw/CMakeLists.txt

## Purpose

`src/rgw/CMakeLists.txt` defines the RADOS Gateway build graph. It configures feature-dependent source lists, generated gperf sources, static libraries, executables, shared librgw output, include paths, compile definitions, dependencies, link libraries, tests, and install rules for RGW components.

## Important APIs, types, and functions

The CMake file requires `gperf`, defines `gperf_generate(input output)`, finds ICU, and conditionally configures Arrow/Parquet/Flight, ISA-L, AMQP, Kafka, DBStore, Motr, DAOS, POSIX, D4N, Jaeger, Lua package, LTTng, curl/OpenSSL, and tests. Main targets are `rgw_common` static library, `rgw_a` static library, `rgw_schedulers`, `radosgw`, `radosgw-admin`, `radosgw-es`, `radosgw-token`, `radosgw-object-expirer`, `rgw-policy-check`, and shared library `rgw`.

`librgw_common_srcs`, `rgw_a_srcs`, scheduler sources, and executable source lists define which `.cc` files participate in each target. `target_link_libraries()`, `target_include_directories()`, `target_compile_definitions()`, `target_compile_options()`, and `add_dependencies()` express integration contracts.

## Control flow

Configuration begins by detecting tools/features and appending source files based on feature flags. `rgw_common` is created first and linked to common Ceph, cls clients, ICU, Lua, RapidJSON, Boost, fmt, OpenSSL, and optional backend/transport libraries. `rgw_a` layers frontend/application sources on top of `rgw_common`. Scheduler, daemon, admin, utility, and shared-library targets then link against these libraries. Generated IAM policy keyword code is produced by `gperf_generate()` and attached to `rgw_iam_policy.cc` through `OBJECT_DEPENDS`.

## State and persistence behavior

The file affects build-system state, not runtime persistence. It writes generated build artifacts such as `rgw_iam_policy_keywords.frag.cc` into the build tree and installs selected binaries/libraries/scripts into configured destinations.

## Dependencies and integration points

It integrates RGW with Ceph common/global libraries, cls clients, librados/libneorados, dmclock, Boost context/url, Lua, RapidJSON, OpenSSL, BLAKE3, ICU, curl, expat, optional Arrow/Flight, OATH, LMDB, RDKafka, RabbitMQ, OpenLDAP, Motr, DAOS, Jaeger, LTTng tracepoint targets, and tests. The conditional source lists mirror RGW's pluggable storage/transport architecture.

## Risks and edge cases

Conditional target creation is complex. `radosgw-admin` is only created under `WITH_RADOSGW_RADOS` or POSIX-without-RADOS, but later Arrow link logic refers to `radosgw-admin` unconditionally under `WITH_RADOSGW_ARROW_FLIGHT`; unusual option combinations could break configuration if the target does not exist. Global `add_definitions()` affects directory scope and may leak feature macros more broadly than target-scoped definitions. Source list drift can silently omit new RGW files from the intended library. Optional dependency order matters for Arrow Flight and linkers.

## Test signals

Validation should include CMake configure/build matrices for default RGW, without RADOS, POSIX, DBStore, D4N, Arrow/Parquet/Flight, Kafka, AMQP, DAOS/Motr, Jaeger/LTTng, and `WITH_TESTS`. Build tests should verify generated gperf output, install target presence, no missing target references, and successful link of all executables/shared libraries.
