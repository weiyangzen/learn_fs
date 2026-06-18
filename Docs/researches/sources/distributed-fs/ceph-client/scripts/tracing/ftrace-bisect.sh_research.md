# sources/distributed-fs/ceph-client/scripts/tracing/ftrace-bisect.sh

Purpose: `ftrace-bisect.sh` helps isolate a function that crashes or hangs the system when enabled under function or function-graph tracing.

Important APIs, types, and functions: it takes `full-file`, `test-file`, and `non-test-file`. It uses `wc -l` to count candidates and `sed` to split the list into first half and second half. Existing output files trigger interactive delete confirmations.

Control flow: if one function remains, it prints that candidate and exits. Otherwise it halves the input line count, checks the input file exists, prompts if output files already exist, then writes lines `1..x` to the test file and `x+1..end` to the non-test file.

State and persistence: writes two candidate files and reads the full candidate list. Users manually move files between iterations based on crash/no-crash outcome.

Dependencies and integration points: designed for manual use with `/sys/kernel/tracing/set_ftrace_filter`, `available_filter_functions`, and `current_tracer`.

Risks: unquoted variables make paths with spaces unsafe. The script counts the file before verifying it exists. Interactive prompts are unsuitable for automation.

Test signals: run against synthetic lists with odd/even counts, one-line inputs, preexisting outputs, and missing input. Manual ftrace workflows are the real integration validation.
