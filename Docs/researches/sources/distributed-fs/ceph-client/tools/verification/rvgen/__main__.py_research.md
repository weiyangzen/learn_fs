# sources/distributed-fs/ceph-client/tools/verification/rvgen/__main__.py

Purpose: `__main__.py` is the installed `rvgen` CLI for generating kernel RV monitors or monitor containers.

Important APIs and flow: argparse defines global `--description` and `--auto_patch`, then subcommands `monitor` and `container`. Monitor generation requires model name, optional parent, class (`da`, `ha`, or `ltl`), spec file, and monitor type from `Monitor.monitor_types`. It dispatches to `da2k`, `ha2k`, or `ltl2k`, or constructs `Container`. `AutomataError` is caught and reported. On success it writes files with `monitor.print_files()` and prints follow-up checklist text for tracepoints, Makefile, Kconfig, and monitor placement.

State and dependencies: output state is a generated monitor directory or direct kernel-tree patches when `--auto_patch` is active. Dependencies are rvgen modules, templates, and writable current/kernel tree. Risks include `params.spec` being referenced in the exception path even for container errors, generated files overwriting existing monitor files through generator writes, and auto-patch marker matching being text-replace based. Test signals are generated files for deterministic, hybrid, LTL, and container modes, plus expected error handling for malformed specs.
