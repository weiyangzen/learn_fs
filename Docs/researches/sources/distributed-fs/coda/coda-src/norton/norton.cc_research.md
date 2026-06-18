# sources/distributed-fs/coda/coda-src/norton/norton.cc

Purpose: main entry point for the interactive Norton recovery shell.

Flow: parses optional `-mapprivate`, requires log device, data device, and length, initializes `/vice` directory handling, calls `NortonInit`, initializes command parsing, enters `Parser_commands`, then terminates RVM and reports its return status.

State/dependencies: sets global `mapprivate` and relies on `NortonInit` to refuse concurrent server use. Dependencies include parser, RVM, and Coda vice directory setup. Risks are minimal argument validation, hard-coded `/vice`, and high privilege/destructive potential once the shell starts. Test signal is startup against valid RVM devices and clean `rvm_terminate`.
