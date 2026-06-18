# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/HelpCommand.java

Purpose: implements top-level and command-specific help for the diskbalancer CLI.

Important APIs/types/functions: constructor registers `-help`. `execute()` accepts null or blank help arguments for generic help, validates options otherwise, normalizes the requested subcommand to lowercase, constructs the corresponding command (`PlanCommand`, `ExecuteCommand`, `QueryCommand`, `CancelCommand`, `ReportCommand`), and delegates `printHelp()`. `printHelp()` uses `HelpFormatter` with `DiskBalancerCLI.getHelpOptions()`.

Control flow: help resolution is a switch over `DiskBalancerCLI` command constants; unknown subcommands fall back to the generic help command. No cluster IO or RPCs occur.

State and persistence behavior: stateless apart from inherited configuration and print stream. It only writes to standard output via Commons CLI formatting.

Dependencies and integration points: depends on all command classes whose help it delegates to, plus `DiskBalancerCLI` option builders. Adding a new diskbalancer command requires updating this switch to expose command-specific help.

Risks: if command constants or option definitions drift, help text can become incomplete. Instantiating real command objects only for help is cheap here but means command constructors must avoid side effects.

Test signals: CLI command tests cover help argument handling indirectly through `DiskBalancerCLI` command parsing.
