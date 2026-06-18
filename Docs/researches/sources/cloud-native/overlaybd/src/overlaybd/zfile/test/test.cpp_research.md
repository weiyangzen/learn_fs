## sources/cloud-native/overlaybd/src/overlaybd/zfile/test/test.cpp

Purpose: GoogleTest coverage for OverlayBD zfile compression, decompression, validation, header/trailer integrity, CRC implementation parity, and streaming builder equivalence.

Important types/functions: `ZFileTest` sets up a `/tmp` local filesystem and helper methods `randwrite`, `seqread`, and `randread`. Tests include `verify_compression`, `validation_check`, `ht_check`, `dsa`, and `verify_builder`. The file directly includes `../zfile.cpp` and `../compressor.cpp`, making it a white-box/integration test rather than pure public API test.

Control flow: `verify_compression` writes random data, then tests checksum disabled/enabled, algorithm values 1..2, and block sizes 4K through 64K. It compresses, opens as zfile, checks sequential and random reads, decompresses, and verifies the decompressed file is not zfile. Validation tests corrupt compressed block data and header/trailer bytes and assert failure. Builder test writes randomly sized chunks through multi-worker and single-worker builders and compares produced zfile bytes.

State/persistence: uses `/tmp/verify.data`, `/tmp/verify.zfile`, and related files through Photon localfs; random seed is fixed in `main`. Photon runtime is initialized once. Dependencies include GTest, GFlags, Photon, zfile, compressor, CRC, and local filesystem.

Risks/test signals: strong signal for block indexing, partial reads, CRC detection, decompression, and ordered multi-worker output. Gaps include no explicit zstd adaptor coverage here, no malformed jump-table fuzzing, no ownership/lifetime assertions, and tests may be relatively expensive due to default `nwrites=16384` and repeated random reads.
