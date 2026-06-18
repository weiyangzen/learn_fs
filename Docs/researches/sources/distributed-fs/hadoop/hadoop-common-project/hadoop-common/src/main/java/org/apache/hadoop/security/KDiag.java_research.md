# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KDiag.java


Purpose: `KDiag` is a command-line Kerberos diagnostics tool for Hadoop. It inspects JVM, OS, configuration, SASL, token, keytab, JAAS, and UGI state and exits with a Hadoop-specific failure code when probes fail.

Important APIs and types: The class extends `Configured`, implements `Tool` and `Closeable`, and exposes `exec(Configuration, String...)`, `main(String[])`, and nested `KerberosDiagsFailure`. Options include `--keytab`, `--principal`, `--keylen`, `--secure`, `--nofail`, `--nologin`, `--jaas`, `--out`, `--resource`, and `--verifyshortname`.

Control flow: `run()` parses options, optionally loads configuration resources, selects output, and invokes `execute()`. `execute()` prints diagnostic sections, validates JCE key length, dumps system properties/environment/configuration, checks whether Hadoop authentication is simple, enables Kerberos/SPNEGO debug temporarily, configures UGI, validates token files, krb5 config/default realm, SASL resolvers, kinit executable, JAAS, NTP config, optional short-name mapping, and optionally logs in from keytab or current login user. Failures go through `verify`, `failif`, and `fail`, which either throw immediately or record `probeHasFailed` under `--nofail`.

State and persistence: Tool state includes output writer, keytab/principal options, min key length, mode flags, and failure flag. It reads local files such as `/etc/krb5.conf`, `/etc/ntp.conf`, keytabs, JAAS config, and token files, but does not persist Hadoop state. It temporarily changes system properties for Kerberos debug and restores them in a finally block.

Dependencies and integration: It depends on Hadoop CLI helpers, UGI, token APIs, keytab utilities, SaslPropertiesResolver, filesystem/configuration constants, Kerberos utilities, and OS/JVM system properties. It is intended for operators troubleshooting secure clusters.

Risks and test signals: Tests should cover argument parsing, `--nofail` accumulation, output file handling, secure-required behavior, keytab login, short-name validation, missing krb5/JAAS/NTP paths, and system-property restoration. Diagnostic output may expose environment and configuration values, so usage should account for sensitive logs.
