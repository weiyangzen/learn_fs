# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectorySecure.java

This secure root-directory contract class mirrors the non-secure Router root test but starts the Kerberized cluster with `RouterHDFSContract.createCluster(true)`.

It returns `RouterHDFSContract` from `createContract` and disables inherited root tests that assume an empty or removable root: empty-root listing, non-recursive root removal, recursive root listing, recursive root removal, and empty-root recursive removal. Those cases do not apply because the Router root exposes federation mount points.

State includes the secure mini-cluster, KDC/SSL artifacts, and Router mount mappings. Dependencies are JUnit, Hadoop root-directory contract tests, and `SecurityConfUtil`.

Integration points are secure Router root listing and mount-point behavior. Risks include losing security-specific root assertions when inherited tests are no-oped, so separate Router-specific tests should cover permission and listing behavior at root. The test signal documents that secure RBF also intentionally diverges from generic empty-root assumptions.
