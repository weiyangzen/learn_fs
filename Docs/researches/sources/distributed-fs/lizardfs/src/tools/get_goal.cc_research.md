# sources/distributed-fs/lizardfs/src/tools/get_goal.cc

Purpose: Implements `lizardfs getgoal` and deprecated `rgetgoal`, reporting storage goal names for objects or recursively for subtrees.

Important APIs/types/functions: `get_goal_run`; `rget_goal_run`; `gene_get_goal_run`; static `get_goal`; `cltoma::fuseGetGoal`; `matocl::fuseGetGoal`; `FuseGetGoalStats`.

Control flow: Parses recursive and formatting flags, opens a read-only master connection, sends typed `fuseGetGoal`, inspects the response packet version, throws on status packets, and prints either one goal name or recursive counts for files and directories per goal.

State and persistence: Read-only master query. Global `humode` controls formatting.

Dependencies and integration: Uses `ServerConnection`, `cltoma` builders, `matocl` deserializers, and common master connection helpers. It is paired with `set_goal.cc`.

Risks and test signals: Normal mode expects exactly one stats entry; protocol changes could break that invariant. Exceptions close the master connection as failed. No direct tests in this subset.
