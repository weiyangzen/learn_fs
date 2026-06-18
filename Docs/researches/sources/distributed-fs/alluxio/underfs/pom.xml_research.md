# sources/distributed-fs/alluxio/underfs/pom.xml

## Purpose
This parent Maven module aggregates Alluxio under file system implementations.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs` and it lists modules including ABFS, ADL, CephFS, COS, GCS, HDFS, local, OSS, Ozone, S3A, Swift, WASB, web, OBS, and TOS. It defines shared properties and shared dependencies such as Guava, Log4j, SLF4J, and test `s3proxy`.

## Control Flow
The build configures shared shade behavior, copy/rename packaging, and clean behavior for UFS modules. Child modules inherit plugin management and dependency versions from this parent and higher Alluxio parent POMs.

## State And Persistence
The POM controls build graph, dependency classpaths, shaded artifacts, and generated/cleaned outputs. It has no runtime state.

## Dependencies And Integration Points
It is the integration point for all underfs modules, including the object-store adapters researched here.

## Risks
Parent-level module ordering and shared plugin behavior affect every UFS. Shading or service metadata mistakes can break discovery at runtime.

## Test Signals
Successful reactor builds and per-module registry tests are the main signals that this parent still assembles UFS modules correctly.
