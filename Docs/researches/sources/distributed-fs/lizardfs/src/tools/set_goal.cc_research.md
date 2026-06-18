# sources/distributed-fs/lizardfs/src/tools/set_goal.cc

Purpose: Implements `lizardfs setgoal` and deprecated `rsetgoal`, changing storage goal names for objects.

Important APIs/types/functions: `set_goal_run`; `rset_goal_run`; `gene_set_goal_run`; static `set_goal`; `cltoma::fuseSetGoal`; `matocl::fuseSetGoal`; option `-l`.

Control flow: Parses formatting, recursive, and long-wait flags, rejects old `+`/`-` goal modifiers, then for each path opens a read-write master connection and sends typed `fuseSetGoal`. It handles status-vs-response packet versions and prints either direct goal result or recursive changed/not changed/not permitted counters.

State and persistence: Mutates master metadata goal assignment. No local persistence.

Dependencies and integration: Uses `ServerConnection`, typed protocol builders, common master connection, and formatting helpers.

Risks and test signals: Changing goals can trigger later replication/deletion work. Long-running recursive changes default to a 30-second timeout unless `-l` is used. No direct tests in this subset.
