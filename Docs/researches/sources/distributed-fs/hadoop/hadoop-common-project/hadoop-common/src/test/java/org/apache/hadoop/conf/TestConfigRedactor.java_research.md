# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigRedactor.java

## Purpose

`TestConfigRedactor` verifies Hadoop's default sensitive-configuration key detection. It confirms that `ConfigRedactor` masks common cloud, filesystem, OAuth, SSL, HTTPFS, and Hadoop security secret keys while leaving nearby non-secret configuration names unchanged.

## Important APIs and types

- `ConfigRedactor(Configuration)` builds the redaction policy from a `Configuration`.
- `ConfigRedactor.redact(String key, String value)` returns `"<redacted>"` for sensitive keys and the original value for non-sensitive keys.
- The test runs with `new Configuration()` and `new Configuration(false)` to cover both default resources and an explicitly empty baseline.

## Control flow

Both public tests delegate to `testRedact`. The helper constructs the redactor, iterates over a curated sensitive-key list, and asserts each value is replaced with `"<redacted>"`. It then iterates over normal keys and asserts the original value is preserved.

## State and persistence behavior

The test is stateless apart from local lists and local `Configuration` instances. It does not persist configuration resources. The main behavior under test is pattern-driven, not value-driven.

## Dependencies and integration points

This file integrates with the default sensitive-key regex used by `ConfigRedactor` and by higher-level configuration dump paths such as `Configuration.dumpConfiguration` and `ConfServlet`. The key list covers S3A, Azure Blob/DFS, ADLS, WebHDFS OAuth, SSL keystores, HTTPFS SSL, and the sensitivity-regex configuration key itself.

## Risks and edge cases

- The test asserts a fixed redaction string; any intentional change to the public redaction marker requires coordinated updates.
- It covers representative key names, not every variant or case-normalization path.
- Because value content is irrelevant, secret-looking values under non-sensitive names are intentionally not redacted.
- False-positive coverage matters: server-side encryption algorithm and keystore location keys must remain visible, while actual key material and passwords must be hidden.

## Test signals

The main signals are two construction modes and paired positive/negative key sets. Additional useful tests would cover custom `hadoop.security.sensitive-config-keys` patterns, case sensitivity, regex metacharacter handling, and integration through servlet/configuration dump output.
