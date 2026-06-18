# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/util/tree.h

## Purpose
Vendored BSD-style intrusive splay tree and red-black tree macro library.

## Important APIs, Types, And Functions
Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, `SPLAY_PROTOTYPE`, `SPLAY_GENERATE`, traversal macros, `RB_HEAD`, `RB_ENTRY`, `RB_PROTOTYPE`, `RB_GENERATE`, `RB_INSERT`, `RB_REMOVE`, `RB_FIND`, `RB_FOREACH`, and min/max helpers.

## Control Flow
Macros generate type-specific tree functions that manipulate caller-embedded left/right/parent/color fields and call a caller-supplied comparator.

## State, Persistence, And Dependencies
No standalone state. Tree nodes and roots are owned by callers. It depends on macro expansion and intrusive struct layout.

## Integration Points
`fuse_connect.c` uses RB macros to maintain the connection cache keyed by username and Kerberos ticket path.

## Risks
Macro code is hard to debug and not type-safe beyond compile-time expansion. Callers must protect trees with locks when used concurrently. Vendored code is excluded from RAT checks.

## Test Signals
Connection cache insert/find/remove/expiry behavior indirectly validates the RB subset used here.
