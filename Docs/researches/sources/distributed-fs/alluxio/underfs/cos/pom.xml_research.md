# Research: sources/distributed-fs/alluxio/underfs/cos/pom.xml

Purpose: Maven descriptor for Alluxio's Tencent Cloud COS native object-store UFS module.

Important APIs and control flow: artifact `alluxio-underfs-cos` depends on `com.qcloud:cos_api:5.6.28`, commons-codec, provided `alluxio-core-common`, and the core-common test jar. Build plugins include maven-shade and copy-rename for distribution packaging.

State, dependencies, integration, risks, tests: build state is shaded Java artifact output. Integration is directly with Tencent COS SDK rather than Hadoop. Risks include SDK version compatibility, transitive dependency conflicts in the shaded artifact, and the need for service metadata to expose `COSUnderFileSystemFactory`. Commons-codec is required for MD5 base64 handling in the output stream.
