# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtUtilShell.java

## Purpose

`DtUtilShell` is the command-line shell for managing Hadoop delegation-token files through `hadoop dtutil`.

## Important APIs, Types, and Functions

It extends `CommandShell`, defines usage and subcommands `help`, `print`, `get`, `edit`, `append`, `cancel`, `remove`, `renew`, and `import`. It parses options `-keytab`, `-principal`, `-renewer`, `-service`, `-alias`, and `-format`.

## Control Flow

`init` optionally performs Kerberos login when both principal and keytab are supplied, selects a subcommand from the first argument, parses command options, records existing token files and first output file, validates format, and lets subcommands validate/execute. Each subcommand delegates to the corresponding `DtFileOperations` method.

## State and Persistence Behavior

Parsed command state is stored in fields for keytab/principal, alias/service/renewer, format, token files, and first file. Persistent token-file writes are performed by `DtFileOperations`.

## Dependencies and Integration Points

It depends on `CommandShell`, `ToolRunner`, `UserGroupInformation` keytab login, `DtFileOperations`, `Configuration`, `Text`, `File`, and SLF4J. It is the CLI entry point.

## Risks and Edge Cases

The parser is positional and increments indices directly, so missing option values can throw. It only adds existing files to `tokenFiles` but preserves the first filename for commands that create output. For HTTP/HTTPS token get, `-service` is required; for non-generic URLs it is rejected.

## Test Signals

Tests should cover each subcommand's validation, missing option values, login with both/one/no Kerberos options, format validation, output-file creation for get/import, generic URL service requirement, and delegation into `DtFileOperations`.
