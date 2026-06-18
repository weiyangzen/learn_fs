# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/HadoopKerberosName.java


Purpose: `HadoopKerberosName` bridges Hadoop configuration to hadoop-auth's `KerberosName` parsing and auth-to-local rule engine.

Important APIs and types: It extends `KerberosName`, has a constructor for full principal strings, and provides static `setConfiguration(Configuration)`. The `main()` helper prints short-name translations for command-line principals.

Control flow and state: `setConfiguration()` selects a default rule based on Hadoop authentication method. Kerberos modes require a resolvable default realm and default to `DEFAULT`; simple modes default to extracting the first component. It then reads `hadoop.security.auth_to_local` and auth-to-local mechanism config and installs them into static `KerberosName` state.

Dependencies and integration: It depends on `SecurityUtil`, `KerberosUtil`, and common configuration keys. UGI and RPC authorization paths rely on these rules to map principals to local user names.

Risks and test signals: Rule state is global in `KerberosName`, and this method does not reset already-set rules beyond calling `setRules`. Tests should cover simple versus Kerberos defaults, missing realm failures, configured rule strings, and mechanism selection.
