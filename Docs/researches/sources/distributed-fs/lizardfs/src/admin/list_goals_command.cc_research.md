<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc

## Purpose
Implements `lizardfs-admin list-goals`, showing master-defined replication/erasure goals.

## Important APIs, Types, and Functions
Defines command methods and supports `--porcelain` and `--pretty`. It uses `SerializedGoal` records and `escapePorcelainString` for goal definitions in porcelain output.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listGoals::build(true)`, deserializes `LIZ_MATOCL_LIST_GOALS`, then prints either simple tabular text, an aligned pretty table, or space-separated porcelain records of ID, name, and escaped definition. It reads master configuration only.

## Dependencies and Integration Points
Depends on goal serialization, master list-goals protocol, `ServerConnection`, and the porcelain escaping helper. Goal output is reused conceptually by chunk health and other admin tooling.

## Risks and Test Signals
Risks include `std::max_element` on an empty goal vector in `--pretty` mode, porcelain escaping applied to definition but not name, and column width using byte length rather than display width. Test signals are empty/nonempty goals, names/definitions with spaces and quotes, pretty table alignment, porcelain parseability, and protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc -->
