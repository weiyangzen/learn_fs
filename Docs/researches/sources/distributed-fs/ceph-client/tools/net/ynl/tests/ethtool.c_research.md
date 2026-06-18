# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.c

Purpose: C selftest for generated ethtool YNL dump bindings, focused on channel and ring queries.

Important APIs/functions: fixture opens `ynl_ethtool_family`. `channels` builds an empty-header dump request (`_present.header = 1`), calls `ethtool_channels_get_dump()`, verifies each entry has `header.dev_name`, and expects at least one RX/TX/combined count. `rings` similarly calls `ethtool_rings_get_dump()` and expects RX or TX ring values.

Control flow/state: empty dumps are skipped. Request structs are stack allocated because they contain only presence metadata and nested header state; returned lists are heap-owned and freed with generated list free helpers.

Dependencies/integration: uses generated `ethtool-user.h`, YNL runtime, kselftest, and wrapper `ethtool.sh` which provides netdevsim.

Risks/test signals: ethtool requires an explicit empty `header` nest, so this test is a good signal for nested presence encoding. It also checks generated dump list parsing and nested header strings. Kernel/device support may cause skips or failures independent of codegen.
