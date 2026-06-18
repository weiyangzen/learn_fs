# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/options/FuseOptions.java

Purpose: immutable-ish holder for Alluxio file system options, normalized FUSE mount options, and update-check enablement.

Important APIs and flow: `create` overloads derive `FileSystemOptions`, collect non-empty `FUSE_MOUNT_OPTIONS` into a set, validate JNR is not used with libfuse3, add `big_writes` for libfuse2, add `direct_io` for JNR/libfuse2, remove unsupported `direct_io` for libfuse3, and add default `max_idle_threads=64` for libfuse3. Getters expose file system options, mutable option set reference, and update-check flag.

State, dependencies, risks, and tests: state is file system options, option set, and boolean. It depends on `AlluxioFuseUtils.getLibfuseVersion`, `FileSystemOptions`, and configuration. Risks include using a set that drops order/duplicates, returning mutable options, silently removing `direct_io` for libfuse3 after logging error, and option normalization changing user intent. Tested indirectly by launcher and filesystem construction paths.
