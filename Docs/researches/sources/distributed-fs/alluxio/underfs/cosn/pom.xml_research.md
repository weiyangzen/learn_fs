# Research: sources/distributed-fs/alluxio/underfs/cosn/pom.xml

Purpose: Maven descriptor for Alluxio's Hadoop COSN UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cosn` sets `ufs.cosn.version` to `3.1.0-5.8.5`, depends on `cos_api-bundle`, `hadoop-cos` at that version, provided core common, `alluxio-underfs-hdfs`, and test jar. Shade filters exclude license/signature files and HDFS factory service metadata. The templating plugin filters `src/main/java-templates` into generated sources, substituting the COSN version constant.

State, dependencies, integration, risks, tests: build state includes generated Java source for `CosnUfsConstants`. Integration relies on Hadoop COS filesystem and Alluxio HDFS underfs base. Risks include keeping `ufs.cosn.version` synchronized with distribution scripts, service metadata conflicts, and generated source availability in IDE/submodule builds.
