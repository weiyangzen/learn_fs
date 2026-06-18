# sources/compression/zstd/contrib/linux-kernel/linux_zstd.h

Purpose: kernel-style wrapper API header around upstream zstd APIs, exposing a stable, lower-case `zstd_*` surface for Linux users while hiding direct upstream symbols.

Important APIs/types: aliases upstream error, memory, dictionary, parameter, context, stream, buffer, frame, and sequence types to kernel names. Declares helper functions for bounds, errors, compression levels, parameter selection, context parameter setting, workspace-bound/init APIs for compression/decompression and streams, one-shot compression/decompression with dictionaries, advanced context/dictionary allocation/free, streaming compress/flush/end/decompress, frame-size/header inspection, external sequence producer registration, and sequence/literal compression.

State and integration: header-only declarations with no state. It includes `linux/types.h`, generated `linux/zstd_errors.h`, and `linux/zstd_lib.h`, and is installed as `linux/include/linux/zstd.h` by the generator. Module wrapper C files provide the definitions and export selected symbols.

Risks and test signals: it must track upstream API changes and kernel consumers' exported-symbol needs. Workspace lifetime requirements are critical in kernel callers. The linux-kernel test build and macro tests are primary signals; actual kernel integration adds ABI/API pressure.
