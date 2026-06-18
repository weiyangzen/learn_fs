# sources/distributed-fs/ceph-client/tools/memory-model/scripts/judgelitmus.sh

Purpose: Judges one litmus output against the expected `Result:` comment or, for hardware runs, against generated LKMM output.

Important APIs and functions: The command API is `judgelitmus.sh file.litmus`. It consumes environment variables `LKMM_DESTDIR` and optionally `LKMM_HW_MAP_FILE`. It parses `Result:` and `DATARACE` annotations, checks output files for `Observation`, unknown macros, timeout status 124, and verification errors, and appends `!!!` or forgiven markers to output files.

Control flow: The script validates the litmus source, determines output filename (`.out` or `.<HW>.out`), determines the expected outcome, reconciles predicted and modeled data-race markers, prints the observation, handles missing observation categories, then compares deadlock and Always/Sometimes/Never outcomes. Hardware Sometimes mismatches and modeled data-race outcome mismatches are forgiven.

State and persistence behavior: It reads source and result files and may append diagnostic lines to the result file. Exit status encodes success, expected mismatch, data-race inconsistency, unknown primitive, timeout, or generic verification failure.

Dependencies and integration points: Used after `runlitmus.sh`/`runlitmushist.sh` to validate results. It depends on herd7 output conventions and LKMM test comments.

Risks: Pattern matching can misclassify nonstandard comments or output. Appending diagnostics makes the output file stateful, so repeated runs can preserve old markers. Hardware data-race modeling is explicitly incomplete.

Test signals: Check litmus files with matching and mismatching `Result:`, `DATARACE`, `DEADLOCK`, unknown macro, timeout, and hardware `Sometimes` cases; verify exit codes and appended diagnostics.
