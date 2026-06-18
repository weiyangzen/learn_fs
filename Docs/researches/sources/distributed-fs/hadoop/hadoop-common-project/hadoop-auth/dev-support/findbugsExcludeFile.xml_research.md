# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion file for intentional representation-exposure warnings in Hadoop Auth secret provider classes.

Important APIs, types, and functions: excludes `EI_EXPOSE_REP` for `getAllSecrets()` and `getCurrentSecret()` on `RolloverSignerSecretProvider`, `StringSignerSecretProvider`, and `FileSignerSecretProvider`.

Control flow: the SpotBugs Maven plugin reads this filter and suppresses matching findings during analysis.

State and persistence: no runtime state. Static-analysis configuration persists in the build tree.

Dependencies and integration points: referenced by `hadoop-auth/pom.xml` in `spotbugs-maven-plugin` alongside the global Hadoop exclude file.

Risks and test signals: suppressing exposed-representation findings assumes callers will not mutate returned byte arrays/secrets; that is a security-sensitive contract. Test signals include SpotBugs runs that suppress only these known patterns while continuing to report other findings.
