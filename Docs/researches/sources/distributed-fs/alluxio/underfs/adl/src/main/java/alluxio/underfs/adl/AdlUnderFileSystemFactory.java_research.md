# Research: sources/distributed-fs/alluxio/underfs/adl/src/main/java/alluxio/underfs/adl/AdlUnderFileSystemFactory.java

Purpose: factory that makes ADL and ADLS URI schemes available to Alluxio's UFS registry.

Important APIs and control flow: `create` checks non-null path and returns `AdlUnderFileSystem.createInstance(new AlluxioURI(path), conf)`. `supportsPath` accepts non-null paths beginning with `Constants.HEADER_ADL` or `Constants.HEADER_ADLS`.

State, dependencies, integration, risks, tests: the class is stateless and thread-safe. Dependencies include Alluxio constants, URI parsing, UFS factory API, and `AdlUnderFileSystem`. Integration depends on module service metadata after shading. Risk is low but scheme-only selection does not validate credential availability or Hadoop ADL library usability at discovery time.
