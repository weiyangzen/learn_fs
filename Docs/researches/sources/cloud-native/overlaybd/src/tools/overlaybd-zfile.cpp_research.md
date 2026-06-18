# sources/cloud-native/overlaybd/src/tools/overlaybd-zfile.cpp

Purpose: standalone zfile utility for compressing, extracting, and verifying OverlayBD zfile blobs, including optional tar adaptor wrapping and stdin streaming.

Important APIs/types/functions: defines `IStreamFile` for stdin reads, `new_streamFile`, `verify_crc`, and uses zfile `is_zfile`, `zfile_validation_check`, `zfile_compress`, `zfile_decompress`, `new_tar_file_adaptor`, and Photon localfs.

Control flow: CLI supports `-x` extract, `--verify`, `-t`, `-f`, algorithm, block size, source, and optional target. Verify mode opens a file or stdin, wraps it in tar adaptor, validates zfile checksum, and exits. Compression can read from stdin when no target path is supplied. Extraction refuses stdin. Compression creates target exclusively and writes zfile data; extraction creates target and writes decompressed bytes.

State and persistence: creates or removes target files depending on `-f`; verify is read-only.

Dependencies/integration: uses Photon runtime and filesystem adaptors with zfile/tar libraries.

Risks: invalid algorithm values other than `lz4`/`zstd` do not explicitly error before compression options are used. Verify always wraps input with tar adaptor, which assumes the expected blob layout. `lseek` on stdin returns `INT64_MAX`, which may surprise generic consumers.

Test signals: cover lz4/zstd compression, extraction, verify valid/invalid blob, pipe compression, extraction pipe refusal, tar adaptor mode, and invalid block size.
