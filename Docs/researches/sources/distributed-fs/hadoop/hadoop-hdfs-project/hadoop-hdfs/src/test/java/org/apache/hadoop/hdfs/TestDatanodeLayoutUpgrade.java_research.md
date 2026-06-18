# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDatanodeLayoutUpgrade.java

Purpose: verifies DataNode on-disk block layout upgrades from historical layouts to the current 32x32 block ID-based layout.

Important APIs and types: `TestDFSUpgradeFromImage`, `MiniDFSCluster.Builder`, `GenericTestUtils.getTestDir`, and fixture tar/checksum files for Hadoop 2.4 and layout -56 images.

Control flow: each test creates a `TestDFSUpgradeFromImage` helper, unpacks a historical DN/NN storage image, sets unmanaged data/name dirs to the unpacked fixture locations, and delegates to `upgradeAndVerify` with one datanode.

State and persistence: unpacks archived NameNode/DataNode directories, configures test data/name storage paths, runs an upgrade startup, and verifies filesystem contents via the shared checksum verifier.

Dependencies and integration: reuses the image-upgrade framework while specifically targeting DataNode layout conversion from LDir and 256x256 ID-based layouts to 32x32.

Risks: dependent on fixture availability and checksum manifest correctness; failure diagnostics are indirect because validation is delegated to shared upgrade verification.

Test signals: successful cluster upgrade and checksum verification for both historical layout inputs.
