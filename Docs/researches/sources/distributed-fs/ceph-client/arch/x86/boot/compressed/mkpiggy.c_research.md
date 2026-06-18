## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mkpiggy.c

### Purpose
`compressed/mkpiggy.c` is a host utility that converts a compressed kernel binary into assembly containing the payload and length symbols needed by the decompressor.

### Important APIs, Types, And Functions
The only function is `main()`. It uses `get_unaligned_le32()` from `tools/le_byteshift.h` and standard C file APIs.

### Control Flow
`main()` requires a compressed-file path, opens it, seeks to the final four bytes, reads the appended uncompressed output length, records the current file length as input length, converts the output length from little endian, and prints assembly defining `.rodata..compressed`, `z_input_len`, `z_output_len`, `input_data`, `input_data_end`, `input_len`, and `output_len` with an `.incbin` directive for the compressed file.

### State, Persistence, And Dependencies
The persistent output is generated assembly on stdout, normally redirected by kbuild to `piggy.S`. It depends on compressor outputs using the kernel `size_append` convention where the uncompressed size is stored in the last four bytes.

### Integration Points
`boot/compressed/Makefile` builds and runs this host program after compression. `misc.c` consumes the generated `input_data`, `input_len`, and `output_len` symbols.

### Risks
The utility assumes the input is seekable and at least four bytes long. Paths are emitted directly in `.incbin`, so build paths with unusual quoting could matter. Any compressor format change to the trailing size convention must update this utility.

### Test Signals
Run on each supported `vmlinux.bin.*` format, verify generated symbol values against file size and appended length, and build with paths containing spaces or special characters if supported by the build environment.
