# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStoragePolicyPermissionSettings.java

Purpose: Tests NameNode storage-policy permission modes: default POSIX-style permission checks, superuser-only enforcement, and global storage-policy disablement.

Important APIs and types: `DistributedFileSystem.setStoragePolicy`, `getStoragePolicy`, `BlockStoragePolicySuite`, `FSNamesystem` fields `isStoragePolicyEnabled` and `isStoragePolicySuperuserOnly`, `ReflectionUtils.setFinalField`, `UserGroupInformation.createUserForTesting`, `DFSTestUtil.getFileSystemAs`, and `LambdaTestUtils.intercept`.

Control flow: Shared cluster setup creates one datanode, default policy suite, COLD policy, a non-admin user, and a supergroup admin. `setStoragePolicyPermissions` mutates final FSNamesystem fields by reflection. `testStoragePolicyPermissionDefault` first denies non-admin on a non-writable file, then chmods to 777 and allows setting COLD. `testStoragePolicyPermissionAdmins` enables superuser-only mode and verifies non-admin denial but admin success. `testStoragePolicyPermissionDisabled` disables storage policies and verifies an IOException while policy remains default.

State and persistence behavior: Tests reuse a static cluster and repeatedly create `/foo`; policy and permission state are stored in NameNode namespace. Reflection mutates global NameNode booleans and can affect subsequent tests if not overwritten.

Dependencies and integration points: Integrates storage policy RPCs, FS permission checking, superuser privilege checks, UGI impersonation, and NameNode internal configuration state.

Risks and test signals: Shared `/foo` and reflected final fields create order sensitivity if a test fails before resetting expected modes. Passing signals policy setting respects configured permission gates and disabled mode.
