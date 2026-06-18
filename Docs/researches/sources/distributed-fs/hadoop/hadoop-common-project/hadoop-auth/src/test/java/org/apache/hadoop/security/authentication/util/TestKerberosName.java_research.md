# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosName.java

Purpose: Tests `KerberosName` principal parsing and rule-based short-name translation for Hadoop and MIT rule mechanisms.

Important APIs and control flow: `setUp()` sets Kerberos realm/KDC system properties and installs a multi-rule Hadoop rule set. `checkTranslation`, `checkBadName`, and `checkBadTranslation` wrap creation and `getShortName()` assertions. Tests cover one-part, two-part, admin/root special rules, anti-pattern principal syntax, Hadoop-vs-MIT unmatched translation behavior, service/host/realm parsing accessors, lower-case `/L` rule suffixes, and invalid mechanism rejection.

State and dependencies: global state includes Java security krb5 system properties and static `KerberosName` rules/mechanism. `@AfterEach` clears the system properties but does not reset rules. Dependencies include `KerberosTestUtils`, IOException behavior, and JUnit.

Integration points: name translation is used by Kerberos authentication handlers to map Kerberos principals to local user names. The tests encode important compatibility between Hadoop-style rules, MIT-style fallback, regex replacements, and lower-casing.

Risks and test signals: global static rule state can interact with other tests if execution order or parallelism changes. The tests intentionally print rules/translations to stdout, useful for diagnostics but noisy. Parsing checks demonstrate accepted forms: service/host@realm, service/host without realm, and service@realm without host.
