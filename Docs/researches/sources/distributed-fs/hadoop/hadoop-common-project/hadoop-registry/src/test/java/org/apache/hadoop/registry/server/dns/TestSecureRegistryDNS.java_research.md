# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestSecureRegistryDNS.java

Purpose: DNSSEC-enabled variant of `TestRegistryDNS`.

Important APIs and functions: overrides `createConfiguration()` to set `KEY_DNSSEC_ENABLED`, public DNSSEC key material, and private key file resource; overrides `isSecure()` to return true.

Control flow: inherits all parent DNS tests, causing `assertDNSQuery()` to expect RRSIG records and doubled answer counts for secure responses.

State and persistence: uses the same dynamic registry DNS state as the parent plus test classpath private key resource.

Dependencies and integration: integrates DNSSEC configuration constants with the entire registry DNS test matrix.

Risks and test signals: high-value regression signal because one subclass exercises many DNS paths with signing enabled. Its key material is static test data; missing `/test.private` resource will fail inherited tests.
