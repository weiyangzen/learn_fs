# sources/distributed-fs/openafs/src/config/lwptool

Purpose: helper script that builds LWP static objects and pthread/libtool objects from the same source list.

Important APIs/types/functions: supports `--mode compile|link`, `--lwpcc`, `--mtcc`, `--linker`, `--ranlib`, `-o`, `--quiet`, and `--` option termination. `_run_cmd` echoes commands unless quiet and fails fast.

Control flow: compile mode maps output `.lo` to hidden `.lwp/*.o`, creates `.lwp`, invokes the LWP compiler for the static object, then invokes the pthread/libtool compiler for the requested object. Link mode maps each `.lo` argument to its `.lwp/*.o` counterpart, removes the target archive, invokes the linker/ar command, and runs ranlib.

State and persistence: creates `.lwp` object mirrors and static archives alongside libtool outputs.

Dependencies and integration: driven by `Makefile.config` `LTLWP_CCRULE` and `LT_LDLIB_lwp` rules. Depends on shell, sed, mkdir, rm, ar/linker, ranlib, and libtool compiler commands.

Risks and test signals: risks include shell-special filenames, missing `.lwp` directory handling, a usage typo in link mode, and naive `.lo` suffix substitution. Signals are hybrid library builds where both libtool `.lo` and LWP archive members are produced and link failures show the failed command.
