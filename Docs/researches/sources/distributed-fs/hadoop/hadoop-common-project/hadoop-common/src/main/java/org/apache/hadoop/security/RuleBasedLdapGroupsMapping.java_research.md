# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/RuleBasedLdapGroupsMapping.java


Purpose: `RuleBasedLdapGroupsMapping` decorates `LdapGroupsMapping` by applying a configured case-conversion rule to LDAP group names.

Important APIs and types: It extends `LdapGroupsMapping`, defines a conversion rule configuration key, supports enum-style rules such as no change, lower-case, and upper-case, and overrides group lookup methods to transform results.

Control flow and state: `setConf()` delegates to LDAP setup, reads the conversion rule, and parses it with `Rule.valueOf(value.toUpperCase())`. Invalid rules are logged, but the field is not explicitly assigned to `NONE`, so a bad value can leave `rule` null and make later switch-based lookups fail. Lookup calls the parent implementation, then maps each group through the selected conversion.

Dependencies and integration: It depends on the full LDAP provider and `StringUtils`/locale-safe case conversion behavior. It is selected as a group mapping provider via Hadoop configuration.

Risks and test signals: Tests should cover lower/upper/noop rules, invalid config values including null-rule behavior after invalid parsing, duplicate group collapse after case conversion, and interaction with nested groups. Case conversion can change authorization semantics in mixed-case LDAP directories.
