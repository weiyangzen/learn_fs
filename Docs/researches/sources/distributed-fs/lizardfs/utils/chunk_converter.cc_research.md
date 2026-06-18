# sources/distributed-fs/lizardfs/utils/chunk_converter.cc

Purpose: command-line converter that rewrites one standard LizardFS/MooseFS chunk into XOR-coded part chunks plus a parity chunk. It accepts `xor_level`, `input_file`, and `output_dir`, validates the XOR level range 2..10, derives output names from the original chunk footer, and emits `chunk_xor_N_of_LEVEL...` plus `chunk_xor_parity_of_LEVEL...`.

Important APIs/functions: `saveBlockAndCrc()` calculates zlib `crc32()` for a 64 KiB parity block, stores the big-endian CRC bytes in a side buffer, writes the parity block, then resets the parity buffer. `main()` owns all parsing, stream setup, header validation, CRC distribution, block distribution, parity construction, and final status reporting.

Control flow: the program reads the 1 KiB header, accepts either `MFSC 1.0` or `LIZC 1.0`, rewrites the signature to `LIZC 1.0`, and sets header byte 20 to the LizardFS XOR chunk type encoding. It then round-robins 1024 4-byte CRC entries across data parts, seeks every part to the block area at 4 KiB, and streams full 64 KiB blocks from the source. Each block is written to its current data part and XORed into the parity accumulator; parity is flushed after every full stripe and once more for a partial final stripe.

State and persistence: persistent output is a set of chunk part files. Writes are direct `std::ofstream` operations with `failbit` exceptions enabled on outputs, but there is no cleanup on partial failure. The input is read sequentially.

Dependencies/integration: depends on `common/platform.h`, zlib, chunk on-disk header offsets, and `ChunkType::getXorChunkType()`-compatible encoding. It is an offline migration/repair utility, not part of the server runtime.

Risks and test signals: risks include assuming fixed 64 KiB block and 1024-block chunk geometry, writing output streams in text mode rather than explicitly binary mode, partial output files after exceptions, and relying on filename length/footer format. Test signals are conversion of old and new signatures, bad headers, xor levels outside 2..10, output-name collision, uneven stripe counts, and CRC/parity validation with the normal chunk verifier.
