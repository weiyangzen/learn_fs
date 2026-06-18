# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/jnifuse/struct/FuseFileInfoTest.java

Purpose: verifies Alluxio JNI `FuseFileInfo` struct offsets match JNR FUSE's `FuseFileInfo` layout for the fields Alluxio depends on.

Important APIs and control flow: the test loads libfuse using `LibFuse.loadLibrary(AlluxioFuseUtils.getLibfuseVersion(Configuration.global()))`, creates `FuseFileInfo` over a 256-byte buffer, creates the JNR struct using a null wrapped pointer, and asserts equal offsets for `flags` and `fh`.

State, dependencies, integration, risks, tests: state is only struct layout metadata. Dependencies include global configuration for libfuse version, `AlluxioFuseUtils`, JNR `Pointer`/`Runtime`, and the external JNR FUSE package. The test protects open flag and file-handle interop. Risk: only two fields are covered, so future Alluxio use of additional native fields would need matching assertions.
