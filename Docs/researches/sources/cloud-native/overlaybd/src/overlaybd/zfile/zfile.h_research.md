## sources/cloud-native/overlaybd/src/overlaybd/zfile/zfile.h

Purpose: public zfile interface for opening, creating, validating, detecting, compressing, and decompressing OverlayBD zfile data through Photon `IFile` objects.

Important APIs: `MAX_READ_SIZE` is 64KiB and bounds zfile block read/decompression buffers. `zfile_open_ro(file, verify, ownership)` returns a read-only decompressed view. `zfile_compress(src, dst, args)` writes a complete compressed zfile. `zfile_decompress(src, dst)` materializes raw bytes. `zfile_validation_check(src)` verifies CRC-enabled zfiles. `new_zfile_builder(file, args, ownership)` returns a streaming writer. `is_zfile(file)` returns 1/0/-1 for zfile/normal/error.

Control flow contract: callers provide already-open Photon files and decide ownership. `verify` controls per-block CRC checking during read; format/header validation always happens during open/detection. Builders require `close()` to finalize index/trailer.

State/persistence: the header declares API only; persistent format details live in `zfile.cpp`. Dependencies are `compressor.h` and Photon file types.

Integration points: used by switch-file fallback/local switch logic, compressor tools, and tests. Risks: C linkage exposes C++ Photon pointer types, so ABI use is effectively project-internal; callers must respect ownership and close semantics or leak/incompletely seal zfiles. Tests in `zfile/test/test.cpp` cover most API paths.
