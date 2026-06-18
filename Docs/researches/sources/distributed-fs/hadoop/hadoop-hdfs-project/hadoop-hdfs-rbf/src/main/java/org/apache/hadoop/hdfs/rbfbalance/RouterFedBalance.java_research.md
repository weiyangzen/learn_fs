# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/RouterFedBalance.java

Purpose: command-line tool for balancing data across Router-Based Federation namespaces by running DistCp, switching the mount-table destination, and then trashing/deleting/skipping source cleanup.

Important APIs and types: extends `Configured` and implements `Tool`; commands `submit` and `continue`; inner `Builder`; `run`, `submit`, `continueJob`, `getSrcPath`, `printUsage`, `getDefaultConf`, and `main`. It uses `FedBalanceContext`, `BalanceJob`, `BalanceProcedureScheduler`, `RouterDistCpProcedure`, `MountTableProcedure`, `TrashProcedure`, and shared fedbalance CLI options.

Control flow: `run` parses CLI options and dispatches to submit or continue. `submit` parses map count, bandwidth, delay, diff threshold, force-close-open, and trash behavior, builds a three-procedure job, submits it to a scheduler, and waits for completion. `continueJob` initializes the scheduler in recovery mode and loops until all jobs report done. `Builder.build` resolves the source mount to an HDFS URI through Router admin APIs, validates the destination has an authority, creates the context with readonly mount handling, then chains DistCp, mount update, and trash procedures.

State and persistence: persistent state is held by `BalanceProcedureScheduler` and serialized procedure contexts. Cluster state changes include copied data, mount-table destination/readonly updates, and source trash/delete behavior.

Dependencies and integration points: integrates Hadoop ToolRunner, fedbalance configuration resources, Router admin address config, mount-table manager, DistCp-based migration, and fedbalance recovery.

Risks: CLI parsing accepts numeric options without range validation beyond downstream behavior. `continueJob` polls forever until jobs complete. `getSrcPath` only supports mounts with exactly one destination. A failed mount-table update or trash step can leave data duplicated or mount readonly. Tests should cover argument validation, destination authority requirement, single-destination source resolution, procedure ordering, scheduler recovery, and trash option parsing.
