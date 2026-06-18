## sources/cloud-native/overlaybd/src/overlaybd/zstd/zstdfile.h

Purpose: public declarations for the ZSTD read adaptor.

Important APIs: `open_zstdfile_adaptor(photon::fs::IFile* file, bool ownership = true)` returns a read-only decompression wrapper and optionally owns the source. `is_zstdfile(photon::fs::IFile* file)` detects a ZSTD magic header.

Control flow contract: consumers should use sequential `read`; the implementation does not support random access operations. Ownership defaults to true, so callers must avoid deleting the wrapped file after handing it to the adaptor.

State/persistence: no state in the header. Dependencies are Photon virtual-file declarations.

Integration points: linked through `zstd_lib`. Risks/test signals: absent tests in the provided subset; detection assumes the file can be read and rewound.
