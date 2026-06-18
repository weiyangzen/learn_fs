# sources/distributed-fs/ceph-client/tools/memory-model/scripts/cmplitmushist.sh

Purpose: Compares historical LKMM/herd7 litmus outputs against freshly generated `.out.new` files and reports whether the observable verification result changed.

Important APIs and functions: `comparetest oldpath newpath` is the only functional API. It detects unknown LKMM macros, timeout status 124, exact output equality after filtering volatile timing/resource lines, identical `Observation` lines, identical `Observation` result classes, and final result changes. The main body builds a temporary shell script from paths read on stdin and executes that generated script.

Control flow: The script creates a private `/tmp/cmplitmushist.sh.$$` directory, defines result counters, transforms each input pathname into `comparetest path.out path.out.new`, sources the generated script, prints per-test output, then emits a stderr summary. It exits nonzero only when a semantic result changed.

State and persistence behavior: State is transient shell counters and temporary comparison files. Persistent inputs and outputs are the caller-provided `.out` and `.out.new` files; this script does not mutate them.

Dependencies and integration points: It is part of the memory-model litmus history workflow, consuming outputs produced by `runlitmushist.sh`/`newlitmushist.sh`. It depends on POSIX shell tools `grep`, `sed`, `awk`, `cmp`, and `expr`.

Risks: The generated shell script is sourced, so unusual filenames from stdin can become shell syntax. Matching is text-pattern based and assumes herd7 output conventions. Timing/resource filtering is intentionally narrow and may not remove all nondeterministic lines.

Test signals: Feed known old/new pairs covering exact matches, count-only matches, Always/Sometimes/Never-only matches, missing observations, unknown macros, timeouts, and changed observations; assert summary counters and exit status.
