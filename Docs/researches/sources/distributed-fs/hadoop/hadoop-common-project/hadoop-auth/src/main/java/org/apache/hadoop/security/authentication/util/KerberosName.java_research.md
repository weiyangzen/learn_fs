<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java

## Purpose
Parses Kerberos principals and applies `auth_to_local` rules to derive local short usernames. It supports Hadoop legacy rule evaluation and MIT-style behavior.

## Important APIs, types, and functions
The constructor parses `service[/host][@realm]`. `setRules()`, `getRules()`, and `parseRules()` manage static rule lists. `setRuleMechanism()` selects `hadoop` or `mit`. `getShortName()` applies rules to the principal components. Inner `Rule` handles `DEFAULT`, `RULE:[n:format](match)s/from/to/[g]/L`, parameter replacement, regex substitution, Hadoop simple-name enforcement, and optional lowercasing. `getDefaultRealm()` lazily obtains the JVM Kerberos default realm through `KerberosUtil`.

## Control flow
Simple names without a realm return immediately. Realm/service/host names become parameter arrays with realm at index 0. Rules are evaluated in order; the first non-null result wins. Hadoop mechanism rejects results containing `/` or `@`; MIT mechanism can return the original full name if no rule matches.

## State and persistence
Rules, rule mechanism, and default realm are static process-wide state. There is no persistence, but setting rules in one filter/test affects later users in the same JVM.

## Dependencies and integration points
Used by `KerberosAuthenticationHandler` and tests to map client Kerberos principals to local users. Depends on regex parsing, locale-aware lowercasing, logging, and `KerberosUtil.getDefaultRealm()`.

## Risks and test signals
Risks include global mutable rule state, regex parsing edge cases, unescaped substitution syntax, null `ruleMechanism` if `getShortName()` is called with no rules, MIT/Hadoop behavior drift, and default realm caching after krb5 config changes. Tests should cover malformed rules, parameter indexes, default rule behavior, lowercasing, global substitutions, non-simple Hadoop rejection, MIT no-match fallback, and reset of default realm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/KerberosName.java -->
