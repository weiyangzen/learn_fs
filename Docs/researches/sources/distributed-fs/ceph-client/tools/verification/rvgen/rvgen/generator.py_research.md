# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/generator.py

Purpose: `generator.py` provides the abstract file/template generation framework for rvgen monitors and containers.

Important classes and methods: `RVGenerator` locates template directories, reads `main.c` and `Kconfig`, tracks name, parent, description, and auto-patch mode, and can locate the kernel `kernel/trace/rv` directory. It fills common template placeholders, emits Kconfig/Makefile/tracepoint tooltips or patches, creates output directories, and writes generated files. `Monitor` extends it with `monitor_types`, loads `trace.h`, fills tracepoint class placeholders, and writes the extra trace header.

Control flow and integration: concrete generators override `fill_model_h()`, monitor class methods, tracepoint skeleton methods, and sometimes Kconfig tooltip behavior. `print_files()` is the main side-effecting entry point used by `__main__.py`.

State and dependencies: output state is local monitor directories or direct kernel-tree modifications. Dependencies are template files, filesystem write permissions, and marker comments in kernel RV files for auto-patching. Risks include mutable default `extra_params={}`, text replacement without duplicate detection, silent reuse of existing directories, overwriting files, no atomic writes, and model names not sanitized for paths/C identifiers. Test signals are correct file sets for monitor/container generators, auto-patch finding intended kernel tree, and generated tooltip text matching manual integration points.
