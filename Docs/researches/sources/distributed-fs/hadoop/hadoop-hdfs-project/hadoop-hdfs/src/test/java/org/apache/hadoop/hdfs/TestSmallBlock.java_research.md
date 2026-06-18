# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestSmallBlock.java

Purpose: Tests HDFS files whose block size and checksum size are smaller than normal client buffers, specifically one-byte blocks for a 20-byte file.

Important APIs and types: `DFSTestUtil.createFile`, `DistributedFileSystem.getFileBlockLocations`, `FSDataInputStream.readFully`, `LocatedBlocks`, `DFSTestUtil.fillExpectedBuf`, and `SimulatedFSDataset`.

Control flow: `testSmallBlock` configures `dfs.bytes-per-checksum` to 1, optionally uses simulated storage, starts a MiniDFSCluster, creates `/smallblocktest.dat` with block size 1 and file size 20, then calls `checkFile`. `checkFile` asserts there are exactly 20 block locations, reads the whole file from offset 0, and compares against either deterministic random bytes or simulated-storage expected bytes. `testSmallBlockSimulatedStorage` toggles the instance flag and reuses `testSmallBlock`.

State and persistence behavior: HDFS stores 20 tiny blocks and associated checksums for the duration of the test. Simulated mode changes expected data derivation because bytes are synthesized from located-block metadata.

Dependencies and integration points: Exercises block-location listing, checksum configuration, client reads over many tiny blocks, and simulated storage dataset integration.

Risks and test signals: The mutable `simulatedStorage` flag is reset after the simulated test; failure to reset could affect later methods in the same instance. Passing signals HDFS correctly handles sub-buffer block/checksum sizes and maps one byte per block.
