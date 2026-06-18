# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRootDirectory.java

This WebHDFS root-directory contract class adapts `AbstractContractRootDirectoryTest` to Router federation and disables generic root assumptions that do not apply.

Lifecycle uses `RouterWebHDFSContract`; `createContract` returns the WebHDFS contract. It no-ops empty root listing, non-recursive root removal, recursive root listing, recursive root removal, empty-root recursive removal, and `testSimpleRootListing`. Comments explain that Router root contains mount points and DFSRouter does not support `LISTSTATUS_BATCH`.

State is the Router WebHDFS mini cluster and mock root mount mapping. Dependencies are JUnit, Hadoop root-directory contract tests, and Router WebHDFS.

Integration points are WebHDFS root listing and Router mount-table behavior. Risks include coverage gaps around root listing, especially because `LISTSTATUS_BATCH` is disabled here. The test signal documents WebHDFS Router root semantics and prevents false failures from generic HDFS root expectations.
