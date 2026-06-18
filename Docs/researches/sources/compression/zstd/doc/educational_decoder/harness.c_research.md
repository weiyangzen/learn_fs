# sources/compression/zstd/doc/educational_decoder/harness.c

Purpose: command-line harness around the educational decoder. It loads a `.zst` file and optional dictionary into memory, chooses an output capacity, invokes `ZSTD_decompress_with_dict()`, and writes the reconstructed bytes to a named output path.

Important APIs/types/functions: `buffer_s`, `read_file`, `write_file`, `freeBuffer`, `ERR_OUT`, `MAX_COMPRESSION_RATIO`, `MAX_OUTPUT_SIZE`, `create_dictionary`, `parse_dictionary`, `ZSTD_get_decompressed_size`, `ZSTD_decompress_with_dict`, and `free_dictionary`.

Control flow: `main` requires `<file.zst> <out_path> [dictionary]`. It reads compressed input and optional dictionary, asks the decoder for frame content size, falls back to `16 * compressed_size` if unknown, caps output at 1 GiB, allocates the output buffer, parses a dictionary unless dictionary support is compiled out, decompresses, frees dictionary state, writes output, and releases all buffers.

State and persistence: state is heap buffers for input, dictionary, and output. Persistent side effect is writing the output file. Error paths call `exit(1)` and may not free all intermediate allocations.

Dependencies/integration: uses `zstd_decompress.h` and the educational decoder implementation, libc file IO, and build-time `ZDEC_NO_DICTIONARY`. It is the executable target used by the Makefile tests.

Risks: `ftell()` result is cast to `size_t` with no negative/overflow check. The fallback compression-ratio assumption can be wrong; too small an output buffer terminates through decoder error paths. `fwrite` loop can spin if `fwrite` returns zero without setting `ferror`. The implementation loads whole files into memory.

Test signals: decode known-size and unknown-size frames, dictionary and raw-content dictionary paths, oversized-output rejection, missing file errors, empty files, and compile/test with and without dictionary support.
