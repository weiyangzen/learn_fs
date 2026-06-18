# sources/distributed-fs/ceph-client/tools/docs/get_abi.py

Purpose: Command-line frontend for parsing ABI documentation, emitting ReST, validating ABI files, searching ABI symbols, and checking undefined sysfs ABI entries on the local machine.

Important APIs, types, and functions: Imports `AbiParser`, `AbiRegex`, `ABI_DIR`, `DEBUG_HELP`, and `SystemSymbols` from tools Python libraries. `AbiRest`, `AbiValidate`, `AbiSearch`, and `AbiUndefined` each register an argparse subcommand and implement `run()`. `main()` sets common debug/dir options, installs subcommands, configures logging, and dispatches.

Control flow: `rest` parses ABI docs, checks issues, and prints generated documentation with optional line markers/raw/no-file behavior. `validate` parses and checks issues only. `search` parses and searches symbols by regex. `undefined` builds regex search data and compares documented ABI symbols against sysfs entries with optional hints, multiprocessing, chunk size, found output, and dry run.

State and persistence: Read-only with respect to ABI docs and sysfs; outputs to stdout/stderr/logging. No files written by this wrapper.

Dependencies and integration points: Depends on `tools/lib/python/abi` modules, kernel ABI documentation tree, sysfs for undefined checks, Python argparse/logging, and optional multiprocessing inside helpers.

Risks: Wrapper behavior is only as stable as helper modules and ABI parser contracts. Undefined checks can be expensive on large sysfs trees. The `--show-hints` option in `rest` is accepted but not used directly here.

Test signals: Run all subcommands against a small ABI dir, search known symbols, validate malformed docs, run undefined with `--dry-run`, `--found`, and `-j` variations.
