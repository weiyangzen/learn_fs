# sources/compression/zstd/contrib/diagnose_corruption/Makefile

Purpose: build recipe for the `check_flipped_bits` corruption-diagnosis utility.

Important behavior: target `all` builds `check_flipped_bits`. It points `ZSTDLIBDIR` at `../../lib`, appends include paths for lib root/common/compress/decompress, enables an extensive warning set, and links `check_flipped_bits.c` with `libzstd.a`. The static library target delegates to `make -C ../../lib libzstd.a`. `clean` removes the binary.

State, dependencies, and integration: build outputs are the local executable and `../../lib/libzstd.a`. It integrates with zstd static-linking-only APIs used by the C file.

Risks and test signals: warnings are strong but not forced to `-Werror` unless `MOREFLAGS` supplies it. The clean target does not remove `.exe` extensions even though the compile target honors `$(EXT)`, which can leave Windows artifacts.
