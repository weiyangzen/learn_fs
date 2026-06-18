# sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.h

Purpose: small public interface for the tar payload adaptor used by Overlaybd remote blob handling.

Important APIs/types/functions: `new_tar_fs_adaptor(photon::fs::IFileSystem*)` returns a filesystem wrapper that auto-wraps opened tar blobs. `is_tar_file(photon::fs::IFile*)` detects a tar header at the beginning of a file. `new_tar_file_adaptor(photon::fs::IFile*)` returns either a tar-offset adaptor or the original file when not tar-wrapped.

Control flow: callers include this header and use the factories; implementation logic lives in `tar_file.cpp`.

State and persistence: the header itself has no state. The factories may produce adaptors that mutate newly created files by writing tar headers/trailers on close.

Dependencies/integration: depends only on Photon filesystem declarations in the header and is used by tar/EROFS tests and remote blob code paths that need to skip tar wrappers.

Risks: comments emphasize this is not a complete tar filesystem implementation; it is for the single-blob tar wrapper format only. Consumers must not expect directory enumeration or multi-entry tar archive semantics.

Test signals: covered by `tar/test/test.cpp::tar_header_check` and indirectly by EROFS tests that include the implementation.
