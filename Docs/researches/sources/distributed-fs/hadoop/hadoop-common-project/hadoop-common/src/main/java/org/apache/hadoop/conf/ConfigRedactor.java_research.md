# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigRedactor.java

Purpose: utility that redacts sensitive configuration values before configurations are displayed in logs, JSON/plaintext, or XML. The source was read as a complete 103-line Java file.

Important APIs/functions: class `ConfigRedactor`; constants `REDACTED_TEXT = "<redacted>"` and `REDACTED_XML = "******"`; field `compiledPatterns`; constructor `ConfigRedactor(Configuration conf)`; public methods `redact(String key, String value)` and `redactXml(String key, String value)`; private `configIsSensitive(String key)`.

Control flow: construction reads `HADOOP_SECURITY_SENSITIVE_CONFIG_KEYS` from configuration with `HADOOP_SECURITY_SENSITIVE_CONFIG_KEYS_DEFAULT`, splits it with `StringUtils.getTrimmedStrings`, compiles each regex, and stores the patterns. Redaction loops over the patterns and returns the redaction token if any regex finds a match in the key; otherwise it returns the original value.

State and persistence: state is an in-memory list of compiled regex patterns per redactor instance. It writes no persistent data and does not mutate the supplied `Configuration`.

Dependencies and integration: depends on `Configuration`, common security config constants from `org.apache.hadoop.fs.CommonConfigurationKeys`, Java regex `Pattern`, and Hadoop `StringUtils`. Used by configuration-dumping paths such as `Configuration.dumpConfiguration` and XML output helpers.

Risks: invalid regexes in configuration throw during construction. Redaction depends only on key names, not value content, so secrets under unexpected keys can leak. Overbroad regexes can hide useful non-secret values. Pattern matching uses `find`, so partial matches are intentional but may surprise administrators.

Test signals: unit tests for default sensitive key patterns, custom regex lists, plaintext versus XML redaction tokens, non-sensitive keys preserving values, invalid regex handling, and integration tests through configuration servlet/dump output.
