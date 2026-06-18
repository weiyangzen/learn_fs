# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/console-badness.sh

Purpose: filters kernel console output for warning, bug, stall, and RCU/KCSAN badness signatures while suppressing known benign lines.

Important APIs and functions: a grep pipeline selects patterns such as `WARNING:`, `BUG`, `Call Trace`, stalls, KCSAN reports, and `!!!`, then removes selected noisy warnings.

Control flow: reads stdin, outputs only suspicious lines not excluded by subsequent filters.

State and persistence: stateless stream filter.

Dependencies and integration: used indirectly by parse-console style tooling in the rcutorture suite.

Risks and test signals: pattern matching is heuristic. It can both miss new failure formats and flag expected test output if filters are stale.
