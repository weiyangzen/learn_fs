# sources/cloud-native/overlaybd/src/overlaybd/tar/tar_file.cpp

Purpose: Photon file/filesystem adaptor for Overlaybd blob files that are physically wrapped in a minimal tar header/trailer but should be exposed to callers as the inner payload file.

Important APIs/types/functions: `TarFile` derives from `ForwardFile_Ownership` and translates all offsets by `base_offset`. `TarFs` derives from `ForwardFS_Ownership` and wraps opened files. Public functions are `is_tar_file`, `new_tar_file_adaptor`, and `new_tar_fs_adaptor`; internal helpers include `new_tar_file`, `open_tar_file`, `strlcpy`, `TarFile::read_header`, `mark_new_tar`, `write_header_trailer`, `is_new_tar`, and `format_pax_record`.

Control flow: `TarFs::open` opens the underlying file and calls `open_tar`. Empty files opened for writing are initialized as new tar blobs with a temporary three-block header. Existing tar files are detected by ustar magic/version/checksum and wrapped. `TarFile::read_header` parses the tar header, records payload size, sets `base_offset` to one block or three blocks if PAX is present, and seeks to payload start. Reads/writes/seeks/fstat/fallocate/fadvise are translated by `base_offset`. On close, a new tar blob is finalized with PAX size record, regular file header, and two zero trailer blocks.

State and persistence: new files are first marked with fake magic/version values and finalized at close. Finalization writes the header at offset zero and trailers at aligned end-of-file. Existing tar files report logical payload size; new tar files report backing size minus header. The underlying `IFile` is owned and closed by the adaptor.

Dependencies/integration: depends on Photon forward file/filesystem wrappers, `TarCore` and `TarHeader` helpers from libtar, POSIX passwd/group lookup for header metadata, and Overlaybd remote blob consumers that need transparent tar skipping.

Risks: `flags & O_RDONLY` is not a reliable read-only test because `O_RDONLY` is zero, so `TarFs::open` may treat read-only opens as write-like and then inspect file size. `TarFile::close` can write headers multiple times if called repeatedly through destructor and user code. `read_header` assumes CachedFile lseek limitations are acceptable. The QED of PAX base offset is hard-coded to three blocks, matching this writer but not arbitrary PAX tars.

Test signals: `tar_header_check` writes through the adaptor, confirms the backing file is a tar, reopens through `new_tar_file_adaptor`, verifies fstat size, pread content, read after seek, and logical SEEK_END behavior.
