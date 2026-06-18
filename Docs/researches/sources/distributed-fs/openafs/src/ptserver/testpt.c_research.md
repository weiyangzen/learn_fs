# sources/distributed-fs/openafs/src/ptserver/testpt.c research

## Purpose
`testpt.c` is a command-driven Protection Server test and stress utility. It validates id usage, name validation, membership correctness, owner-chain behavior, and large membership mutation scenarios against a live ptserver.

## Important APIs, types, and functions
Command handlers are `ListUsedIds`, `TestPrServ`, and `TestManyMembers`. `ListUsedIds` scans user or group id ranges with `pr_IdToName` and compares returned names to numeric ids to classify used/free ids. `TestPrServ` validates name length and illegal-character behavior for users and groups, creates/deletes entries, and confirms creator lookup. `TestManyMembers` creates many users and groups, adds/removes memberships according to a generated matrix, validates membership and CPS results, validates owner lists, then deletes entries.

Supporting functions include `IdCmp`, `GetGroupLimit`, `CreateUser`, `CreateGroup`, `DeleteRandomId`, `AddUser`, `RemUser`, `ka_ConvertBytes`, and command before/after procs `MyBeforeProc`/`MyAfterProc`. `add_std_args` provides test configuration options for confdir, cell, noauth, and server list.

## Control flow, state, and persistence
`MyBeforeProc` builds or opens AFS configuration for tests. If a confdir is not supplied, it creates temporary CellServDB/ThisCell/NoAuth files derived from local config and command arguments. `MyAfterProc` removes those temporary files. Tests initialize libprot against that config and then perform real ptserver operations.

`TestManyMembers` builds arrays for users, groups, group owners, and a `number x number` membership matrix. It randomly creates entries, adds memberships, removes some memberships, verifies server lists against the matrix with either `ubik_PR_ListElements` or `ubik_PR_GetCPS`, checks expected CPS extras, checks that groups appear on the correct owner chains, and cleans up by deleting random remaining ids.

## Dependencies and integration points
The file depends on `ptuser.h`, generated `ptclient.h`, command parsing, AFS auth/config/token APIs, Rx/XDR, and PT/Rx/KTC error tables. It directly calls both public libprot APIs and generated `ubik_PR_*` functions, making it useful for testing client wrappers and server RPC behavior.

## Risks and test signals
Because it mutates a real protection database, it should be run only against test cells or disposable databases. Randomized ownership and membership patterns are valuable for continuation blocks, owner chains, and reciprocal membership consistency, but failures terminate with `exit`, so harnesses should isolate runs. Important coverage includes boundary-length names, illegal characters, duplicate handling, large CPS/list elements, owner lists, group deletion, id-range scanning, noauth temporary config, and reproducibility through the `-seed` argument.
