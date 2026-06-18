<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_feat.py -->
# sources/distributed-fs/ceph-client/tools/docs/get_feat.py

Purpose: CLI front end for parsing `Documentation/features` feature files and rendering architecture support information as ReST tables or machine-readable lists.

Important APIs/types/functions: `GetFeature` owns the command implementation. `get_current_arch()` normalizes `uname -m` values (`x86_64`/`i386` to `x86`, `s390x` to `s390`). `run_parser()` constructs `feat.parse_features.ParseFeature`. `run_rest()`, `run_current()`, `run_list()`, and `validate_args()` drive parser output. `parser()` builds argparse subcommands `current`, `rest`, `list`, and `validate` plus shared `--directory`, `--debug`, and `--enable-fname`.

Control flow: `main()` parses command-line arguments, requires a subcommand, then dispatches to the function stored in `args.func`. All output flows through `ParseFeature` methods: matrix, per-architecture table, single-feature view, validation-only parse, or list output.

State and persistence: No persistent state is created. Runtime state is the parsed feature tree and the mutable argparse namespace, where `run_current()` and `run_list()` may fill in `args.arch` from the host architecture.

Dependencies/integration: Imports kernel-local `tools/lib/python/feat/parse_features.py` by adding `../../tools/lib/python` relative to this script. It integrates with documentation builds through ReST output and with dependency tracking through `--enable-fname`.

Risks/tests: Risks are stale architecture normalization, missing `get_feat.pl` compatibility expectations from callers, and parser failures hidden behind ReST generation. Test signals include `validate` over the default feature directory, `rest` for all/arch/feature combinations, `list --arch`, and current-architecture behavior on x86 and s390 hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/get_feat.py -->
