# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfTest.java

Purpose: `ConfTest` is the `hadoop conftest` validator for Hadoop XML configuration files, checking structural correctness and duplicate properties.

Important APIs and types: `checkConf(InputStream)` returns validation errors. `main` parses `-conffile`, `-h`, and `--help`. Private `parseConf` uses StAX. Package-private `NodeInfo` records property attributes/elements and duplicate QName data.

Control flow: `main` first uses `GenericOptionsParser`, then Commons CLI for specific options. It selects explicit files/directories or `${HADOOP_CONF_DIR}` XML files, validates each, prints valid/errors, and exits nonzero if any invalid. `checkConf` parses top-level `<configuration>`, validates direct children are `<property>`, requires `<name>` and `<value>`, detects empty names and duplicate property names, and flags duplicated child elements except `<source>`.

State and persistence behavior: reads XML files and environment variables; writes stdout/stderr only. `NodeInfo` stores parse state in memory.

Dependencies and integration points: depends on StAX, Commons CLI, `GenericOptionsParser`, Hadoop `StringUtils`, and shell command integration.

Risks: `-h/--help` option is declared with `hasArg`, which can make help parsing unintuitive. The parser tracks first text for elements and may not fully model complex XML. `terminate` calls `System.exit` directly rather than `ExitUtil`.

Test signals: cover valid config, wrong root, non-property children, missing/empty name, missing value, duplicate names, duplicate child elements, allowed duplicate source, directory selection, missing `HADOOP_CONF_DIR`, and CLI parse errors.
