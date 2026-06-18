# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/fifo.json

Purpose: 16 FIFO-family tests for `bfifo`, `pfifo`, invalid handles/arguments, replace, duplicate/delete failures, invalid handle syntax, and `pfifo_head_drop` limit-zero behavior.

APIs and control flow: Uses `$TC qdisc add|replace|del|show` plus `ping` for drop-counter testing. Positive cases verify byte/packet limits; negative cases validate parser/kernel rejection.

State/dependencies: State is root FIFO qdisc configuration and packet/drop counters. Requires base FIFO qdiscs, namespace dummy device, and ping.

Risks/test signals: Exit codes span `0`, `1`, `2`, and `255`, so validation layer changes can affect results. Regexes distinguish `b` vs `p` units and expect `dropped 2` for head-drop.
