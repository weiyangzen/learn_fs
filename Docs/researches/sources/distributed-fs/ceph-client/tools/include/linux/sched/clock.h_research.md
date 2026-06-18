<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h

## Purpose
This is an empty tools compatibility header for scheduler clock includes.

## APIs And Flow
It exports only an include guard and no `sched_clock()`, `cpu_clock()`, or local clock functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is limited to sources where scheduler clock APIs are compiled out or supplied elsewhere. The risk is compile failure if imported code starts using kernel clock helpers. Test signal is building all current tools consumers and grepping for unresolved scheduler clock symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/clock.h -->
