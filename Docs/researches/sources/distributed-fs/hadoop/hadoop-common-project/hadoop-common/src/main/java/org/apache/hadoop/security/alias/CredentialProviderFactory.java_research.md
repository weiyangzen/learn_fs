# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/alias/CredentialProviderFactory.java

Purpose: ServiceLoader-backed factory that turns configured credential provider URI paths into concrete `CredentialProvider` instances.

Important APIs/types/functions: `CREDENTIAL_PROVIDER_PATH` config key, abstract `createProvider(URI, Configuration)`, static `getProviders(Configuration)`, static `serviceLoader`, and `SERVICE_LOADER_LOCKED` recursion guard.

Control flow: static initializer eagerly iterates ServiceLoader to avoid lazy-loading synchronization races. `getProviders` iterates every configured URI string, parses it, synchronizes on ServiceLoader, sets recursion guard, asks each factory to create a provider, and adds the first non-null match. Bad URI syntax and unknown schemes become IOExceptions; recursive loads become `PathIOException`.

State/persistence: static ServiceLoader and atomic recursion guard. No persistence.

Dependencies/integration: providers register factories through Java ServiceLoader; Hadoop `Configuration` supplies comma/string collection provider paths; `PathIOException` reports recursive filesystem credential loading.

Risks: synchronized global ServiceLoader can serialize provider creation; recursion guard is global and can reject nested loads; factory ordering controls scheme resolution; unknown provider path aborts the whole call. Test signals include multiple configured paths, bad URI, unknown scheme, recursive load guard, concurrent access, and first-match factory behavior.
