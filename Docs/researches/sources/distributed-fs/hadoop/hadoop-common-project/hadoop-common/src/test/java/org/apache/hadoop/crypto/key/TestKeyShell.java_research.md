# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyShell.java

## Purpose
`TestKeyShell` validates the command-line key management tool against a temporary JCEKS provider, including lifecycle operations, warnings, strict mode, cipher options, descriptions, and attributes.

## Important APIs, Types, and Functions
It uses `KeyShell.run(String[])`, `KeyShell.NO_VALID_PROVIDERS`, `ProviderUtils` password warning/error strings, and `KeyProviderFactory.KEY_PROVIDER_PATH`. Helpers `deleteKey()` and `listKeys()` execute shell commands and assert return codes/output.

## Control Flow
`setup()` creates a unique temp directory, builds a `jceks://file...` provider URI, and redirects stdout/stderr to byte buffers. Tests run CLI commands for `create`, `list`, `roll`, `invalidateCache`, and `delete`. Negative tests cover invalid key size, invalid cipher, invalid provider, transient-provider-only configuration, strict no-password mode, malformed attributes, and duplicate attributes.

## State and Persistence
The test writes an actual JCEKS keystore in a temp directory. It also mutates JVM-global `System.out` and `System.err` during each test and restores them in `cleanUp()`.

## Dependencies and Integration Points
Dependencies include `KeyShell`, `Configuration`, `Path`, `ProviderUtils`, `GenericTestUtils`, local file-backed JCEKS, and JUnit. It bridges command-line parsing with provider lifecycle operations and user-facing output strings.

## Risks and Edge Cases
Output assertions are sensitive to wording changes. Strict mode and no-password warnings protect users from insecure provider setup. Attribute parsing trims whitespace, allows values containing `=`, rejects missing names/values, and rejects repeated attribute names.

## Test Signals
Passing tests signal successful CLI create/list/roll/invalidate/delete flows, metadata display, description support, invalid-option failures, transient-provider warnings, strict password enforcement, full cipher names, and robust attribute parsing.
