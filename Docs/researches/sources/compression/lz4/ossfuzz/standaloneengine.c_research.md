# sources/compression/lz4/ossfuzz/standaloneengine.c

## Purpose
`standaloneengine.c` provides a minimal command-line runner for fuzz targets when libFuzzer or another fuzzing engine is not linked.

## Important APIs, Types, And Functions
The only function is `main()`. It opens each filename argument, reads the whole file into a heap buffer, and calls `LLVMFuzzerTestOneInput(buffer, buffer_len)` from `fuzz.h`.

## Control Flow
For each argument, the runner prints the file name, opens it in binary mode, seeks to the end to get length with `ftell()`, seeks back, allocates a zeroed buffer with `calloc()`, reads the full file, invokes the fuzzer, frees the buffer, closes the file, and continues to the next argument. Open and allocation failures are reported to stderr.

## State, Persistence, And Dependencies
State is local file handles and heap buffers. It does not write files or maintain corpus state. It depends on standard C file I/O and allocation.

## Integration Points
The OSS-Fuzz Makefile links this object into every fuzzer when `LIB_FUZZING_ENGINE` is empty, enabling local reproduction with `./target_fuzzer corpus_file`.

## Risks
The code does not check `fseek()`, `ftell()` errors, or short `fread()` results. `ftell()` is stored in `size_t`, which can mishandle negative errors and very large files. Empty files allocate zero bytes with `calloc(0, ...)`; if that returns null, the fuzzer is skipped.

## Test Signals
Run a standalone fuzzer against existing corpus files, missing paths, empty files, and large files. Sanitizer runs can catch allocation and file-size edge cases.
