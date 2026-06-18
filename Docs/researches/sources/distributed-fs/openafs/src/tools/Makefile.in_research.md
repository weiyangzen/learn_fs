# sources/distributed-fs/openafs/src/tools/Makefile.in

Purpose: top-level make dispatcher for the OpenAFS `src/tools` subtree.

Important targets and control flow: defines `SUBDIRS=dumpscan rxperf`. For `all`, `dest`, `install`, `clean`, and `distclean`, it loops over each subdirectory, runs `$(MAKE) $@`, and exits immediately if a child make fails.

State and dependencies: it does not build artifacts directly; persistence is delegated to child makefiles. It depends on make variables expanded by configure, a shell, and child directories with compatible targets.

Integration points: this file connects the main OpenAFS build to `dumpscan` and `rxperf`. A failure in `dumpscan/Makefile.in` or `rxperf` propagates through the `|| exit 1` guard.

Risks/test signals: the `cd $$A && $(MAKE) ... && cd ..` pattern assumes all subdirectory names are simple and that returning to `..` is sufficient. Build signal is coarse: success means all child targets returned zero.
