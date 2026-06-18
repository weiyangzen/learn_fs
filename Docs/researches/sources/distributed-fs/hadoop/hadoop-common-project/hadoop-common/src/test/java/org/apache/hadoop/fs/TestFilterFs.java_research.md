## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFilterFs.java

Purpose: verifies that `FilterFs` implements the required `AbstractFileSystem` delegation surface and can wrap an AFS whose authority is optional, such as ViewFs.

Important APIs/types/functions: `FilterFs`, `AbstractFileSystem`, reflection, `DontCheck` exclusions, `ConfigUtil.addLink`, `FileContext.getFileContext`, and ViewFs URI `viewfs://custom/`.

Control flow: `testFilterFileSystem` iterates non-static/non-private/non-final methods declared on `AbstractFileSystem`; unless listed in `DontCheck`, each must be declared on `FilterFs`. `testFilteringWithNonrequiredAuthority` configures a ViewFs link and constructs an anonymous `FilterFs` over the default AFS.

State and persistence: uses only configuration and FileContext/AFS objects. No files are written.

Dependencies/integration points: protects API parity for AbstractFileSystem wrappers and integration with ViewFs mount-table configuration where authorities are not always required like ordinary schemes.

Risks and test signals: reflection failures indicate wrapper drift after adding or changing AFS methods. The ViewFs wrapping test guards against over-strict authority validation in filter constructors.
