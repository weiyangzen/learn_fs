# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialShell.java

Purpose: command-line implementation for `hadoop credential`, exposing list, create, check, and delete operations over configured credential providers.

Important APIs/types/functions: `init` parses subcommands and flags (`-provider`, `-f`, `-strict`, `-value`, `-help`). Inner `Command` selects provider, preferring first non-transient provider unless user supplied provider explicitly. `ListCommand`, `DeleteCommand`, `CheckCommand`, and `CreateCommand` implement validation and execution. `promptForCredential` double-prompts and clears mismatched buffers. `PasswordReader` wraps `System.console`.

Control flow: parsed subcommand validates provider and password requirements. `create` prompts or uses test value, creates entry, flushes. `delete` confirms unless forced, deletes, flushes. `check` reads supplied/prompted value and compares to stored char[] with `Arrays.equals`. `list` prints aliases. Strict mode fails when a provider needs a password but none was supplied; non-strict prints warning.

State/persistence: shell instance tracks interactivity, strictness, user-supplied provider flag, test value, and password reader. Persistence occurs through provider `flush`.

Dependencies/integration: `CommandShell`, `ToolRunner`, `CredentialProviderFactory`, provider implementations, console IO, and Hadoop generic options.

Risks: `-value` exposes secrets through command line and is marked testing-only but parsed generally; console absence fails create/check; transient provider modification is allowed with warning; provider selection can surprise when `user:///` appears before durable stores unless filtered. Test signals include argument parsing, strict/non-strict password-required handling, no valid providers, forced delete, prompt mismatch clearing, check success/failure/missing alias, and command help paths.
