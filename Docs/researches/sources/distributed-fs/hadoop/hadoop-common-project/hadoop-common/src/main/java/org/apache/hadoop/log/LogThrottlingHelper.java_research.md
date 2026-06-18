## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogThrottlingHelper.java

Purpose: Thread-safe helper that lets callers throttle repeated log statements while retaining per-window summary statistics for numeric values. It does not log directly; it returns a `LogAction` telling the caller whether to emit.

Important APIs/types/functions: `LogAction` exposes `shouldLog()`, `getCount()`, and `getStats(int)`. Constructors accept a minimum log period and optional primary recorder name. `record(double...)` records under the default name; `record(String,long,double...)` coordinates named recorders. `getCurrentStats`, `getLogSupressionMessage`, and testing-only `reset` expose state.

Control flow: `record` assigns the first recorder as primary if needed, records values into a `LoggingAction`, checks elapsed monotonic time for the primary, and marks all current actions loggable when the primary fires. Dependent recorders log only after the primary has triggered and before the primary state is consumed.

State and persistence: Maintains `minLogPeriodMs`, `primaryRecorderName`, `lastLogTimestampMs`, a `Timer`, and a map of current `LoggingAction` instances containing counts and `SummaryStatistics`. State is in-memory only and guarded by synchronized methods.

Dependencies/integration: Uses Hadoop `Timer`, Apache Commons Math `SummaryStatistics`, and Hadoop testing annotations. Integrates with any caller-side logger.

Risks/test signals: Incorrect value arity raises errors through `LoggingAction`; callers must not read `DO_NOT_LOG` stats. Tests should cover primary/dependent ordering, reset, elapsed-time boundaries, stat aggregation, and suppression message grammar.
