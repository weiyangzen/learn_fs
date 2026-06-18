# sources/distributed-fs/alluxio/underfs/wasb/pom.xml

## Purpose
This Maven module packages the Microsoft Azure Blob Storage UFS implementation as `alluxio-underfs-wasb`.

## Important Configuration
The module inherits from `alluxio-underfs`, sets `ufs.hadoop.version` to `3.3.4`, and depends on `hadoop-azure`, provided `alluxio-core-common`, and `alluxio-underfs-hdfs`. Test dependencies include Apache commons-lang3 and Alluxio common test jar.

## Build and Integration
The shade plugin packages dependencies while excluding license/signature metadata and excluding HDFS UFS factory service entries because the module depends on the HDFS UFS implementation but should not register HDFS from this artifact. The copy-rename plugin follows Alluxio UFS packaging conventions.

## Risks and Test Signals
The module is tightly coupled to Hadoop Azure filesystem implementation class names. Shading exclusions are important; if HDFS factory metadata leaks into the WASB artifact, registry behavior can change. The module's tests focus on factory support rather than full Azure integration.
