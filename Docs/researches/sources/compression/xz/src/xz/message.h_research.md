# Research: sources/compression/xz/src/xz/message.h
## sources/compression/xz/src/xz/message.h

Purpose: Declares the messaging, verbosity, progress, help, and liblzma error-reporting interface.

Important APIs and types: `enum message_verbosity` defines silent, error, warning, verbose, and debug levels. The header exports progress signal list, initialization, verbosity controls, formatted message variants with printf attributes, fatal/bug/signal helpers, `message_strm()`, memory/filter display, help/version functions, file count/name registration, and progress lifecycle calls.

Control flow and integration: All modules use this API for diagnostics. `coder.c` owns the progress lifecycle. `main.c` initializes messages and sets file counts. `args.c`, `hardware.c`, `file_io.c`, `list.c`, `sandbox.c`, and `options.c` call fatal/error/warning helpers.

State and persistence: State is internal to `message.c`; callers must only respect progress start/end pairing.

Risks: Format-string attributes help compile-time checking, but translated strings and variadic calls still need care. `message_progress_start()` must follow `message_filename()` and must end before the stream becomes invalid.

Test signals: Compile with format warnings, run progress lifecycle tests, and verify message calls update exit status through `main.c` as expected.
