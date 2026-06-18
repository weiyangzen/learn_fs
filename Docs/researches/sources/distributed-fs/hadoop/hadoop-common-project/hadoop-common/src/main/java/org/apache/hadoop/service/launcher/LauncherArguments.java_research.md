# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/LauncherArguments.java

Purpose: `LauncherArguments` centralizes the command-line option names and parse-error text shared by the service launcher package.

Important APIs and types: it defines constants for `--conf`, short `conf`, `--hadoopconf`, short `hadoopconf`, and the parse failure prefix `E_PARSE_FAILED`.

Control flow: `ServiceLauncher.createOptions` uses these constants to build Commons CLI options, while parse failures use `E_PARSE_FAILED` in `ServiceLaunchException` messages.

State and persistence behavior: this is a constant-only interface with no runtime state or persistence.

Dependencies and integration points: consumed by `ServiceLauncher` and documented by `LauncherExitCodes`/package docs. The names mirror a subset of Hadoop `GenericOptionsParser` options but are intentionally restricted by `MinimalGenericOptionsParser`.

Risks: changing these strings breaks launcher compatibility and command help. The short option values are identical to long names, so parser behavior depends on Commons CLI accepting that spelling.

Test signals: assert option creation includes the expected names, parse errors include `Failed to parse:`, and usage text remains synchronized with these constants.
