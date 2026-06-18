# Research: sources/distributed-fs/alluxio/underfs/cosn/src/main/java-templates/alluxio/CosnUfsConstants.java

Purpose: Maven-filtered Java template that exposes the COSN Hadoop UFS version compiled into the module.

Important APIs and control flow: class `CosnUfsConstants` is final, has public static final `UFS_COSN_VERSION = "${ufs.cosn.version}"`, and a private constructor. During the Maven templating phase, the placeholder is replaced with the module property, e.g. `3.1.0-5.8.5`.

State, dependencies, integration, risks, tests: no runtime state. Integration point is `CosNUnderFileSystemFactory.getVersion`, which uses this constant for version-aware factory selection when `UNDERFS_VERSION` is set. Risk: if templating does not run, the literal placeholder may appear in compiled code or IDE analysis; version drift can prevent factory discovery for explicitly versioned mounts.
