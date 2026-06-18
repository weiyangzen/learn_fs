# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/alias/TestCredShell.java

Purpose: tests the `CredentialShell` command-line lifecycle and validation behavior for creating, listing, checking, deleting, help output, invalid providers, transient providers, prompting, and strict password enforcement.

Important APIs and types: `CredentialShell`, `CredentialShell.PasswordReader`, `CredentialProviderFactory.CREDENTIAL_PROVIDER_PATH`, `ProviderUtils` warning/error constants, `Configuration`, `Path`, `GenericTestUtils.getTestDir`, and `ByteArrayOutputStream`.

Control flow: setup redirects `System.out` and `System.err` to buffers, deletes the test keystore, and builds a JCEKS provider URI. Lifecycle tests run `create`, `list`, `delete`, and `list` again against the same provider, asserting return codes and output. Invalid/transient provider tests verify no-provider and warning messages. Prompt tests inject `MockPasswordReader` values to simulate mismatched, missing, successful, and failed password checks. Argument tests call `init` directly for empty args, command help, and missing command operands. Strict mode verifies that missing provider password becomes an error rather than a warning. Help tests assert usage output.

State and persistence: writes a JCEKS keystore under `GenericTestUtils.getTestDir("creds")`, redirects global `System.out/err` without restoring them in the test class, and mutates the in-memory user provider for `user:///` cases.

Dependencies and integration points: exercises the CLI facade over credential providers, provider password warning policy, Hadoop configuration, filesystem-backed JCEKS persistence, and interactive password reader abstraction.

Risks: global stream redirection can affect neighboring tests. One password-failure branch appears to create `passwordError` but passes the previous `password` list, so its intended mismatch may be weaker than the assertion suggests. Keystore files persist between tests unless setup deletion is complete.

Test signals: validates user-facing CLI return codes and messages, lifecycle persistence, transient-provider warnings, strict mode enforcement, prompt handling, and basic command parser behavior.
