# sources/distributed-fs/alluxio/underfs/ozone/pom.xml

## Purpose
This Maven descriptor builds the Apache Ozone under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-ozone`. It pins `ufs.ozone.version` to `1.2.1`, declares Ozone client/filesystem dependencies, metrics, provided logging dependencies, `alluxio-core-common`, and `alluxio-underfs-hdfs`.

## Control Flow
Profiles choose `ozone-filesystem-hadoop2` or the default active `ozone-filesystem-hadoop3`. The build shades dependencies, relocates `com.google` to `alluxio.shaded.hdfs.com.google`, filters metadata/license artifacts, excludes the HDFS UFS service file, and runs templating for generated constants.

## State And Persistence
The POM controls build artifacts and generated source constants; it has no runtime state.

## Dependencies And Integration Points
Ozone implementation extends the HDFS UFS, so this module depends directly on the HDFS underfs module and Ozone's Hadoop filesystem artifacts.

## Risks
Dependency conflicts are likely around Hadoop/Ozone/Guava/metrics, making shading and service-resource filtering important. Hadoop profile selection affects runtime compatibility.

## Test Signals
Build success checks dependency resolution, shade configuration, and generated `OzoneUfsConstants`.
