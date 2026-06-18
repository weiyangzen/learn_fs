# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ToolRunner.java

Purpose: `ToolRunner` executes `Tool` implementations after generic Hadoop option parsing, while setting common CLI audit/caller context.

Important APIs/types/functions: `run(Configuration, Tool, String[])` is the main entrypoint. `run(Tool, String[])` delegates using the tool's existing configuration. `printGenericCommandUsage(PrintStream)` delegates to `GenericOptionsParser`. `confirmPrompt(String)` repeatedly reads from `System.in` until it receives yes/no input.

Control flow: `run` installs a default `CallerContext` of `CLI` if absent, notes the tool in `CommonAuditContext`, creates a new `Configuration` when needed, parses generic options with `GenericOptionsParser`, sets the resulting configuration on the tool, then invokes `tool.run` with remaining arguments. `confirmPrompt` writes to stderr, reads characters until newline/EOF, accepts y/yes or n/no case-insensitively, and loops on invalid input.

State and persistence behavior: modifies static/thread-local caller context and audit context, mutates the tool's configuration reference, and consumes process stdin for prompts.

Dependencies and integration points: depends on `Configuration`, `GenericOptionsParser`, `CallerContext`, and `CommonAuditContext`. It is the standard launcher path for Hadoop CLI tools.

Risks: `tool` is not null-checked. `confirmPrompt` can block forever on non-interactive input that is not EOF and can repeatedly emit invalid input messages. Caller context is only set when absent; nested invocations inherit existing context.

Test signals: tests should verify generic options removal, configuration mutation, caller/audit context behavior, and prompt parsing for yes/no/invalid/EOF paths.
