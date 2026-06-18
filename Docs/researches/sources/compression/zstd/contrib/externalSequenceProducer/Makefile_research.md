# sources/compression/zstd/contrib/externalSequenceProducer/Makefile

Purpose: build recipe for the external sequence producer example program.

Important behavior: defines `PROGDIR`, `LIBDIR`, and `LIBZSTD`, includes lib root/compress/common headers, uses GNU99 plus broad warning flags, and builds `externalSequenceProducer` from `sequence_producer.c`, `main.c`, and `libzstd.a`. The library target delegates to `make -C ../../lib libzstd.a CFLAGS=...`; `clean` removes local objects, cleans the lib directory, and removes the executable.

State, dependencies, and integration: local executable/object files and `../../lib/libzstd.a` are build state. It integrates with zstd static-linking-only sequence producer APIs and internal compression headers.

Risks and test signals: cleaning the shared lib directory can affect other concurrent builds. The example is built by top-level contrib target, which serves as the main regression signal for API compatibility.
