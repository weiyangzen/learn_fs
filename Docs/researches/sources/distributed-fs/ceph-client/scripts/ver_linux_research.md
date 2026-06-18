# sources/distributed-fs/ceph-client/scripts/ver_linux

Purpose: `ver_linux` is an awk utility that prints versions of system tools relevant to kernel compilation and installation, along with the running kernel and loaded modules.

Important APIs, types, and functions: the `BEGIN` block defines regexes, prints a note pointing to `Documentation/process/changes.rst`, runs `uname -a`, then calls `printversion(name, version(command))` for many tools. `version(cmd)` executes a command, returns the first version-like number matched in its output, and closes the pipe. `printversion()` formats non-empty values. It also scans `ldconfig -p` for libc/libstdc++ paths and `/proc/modules` for loaded modules.

Control flow: all work happens during awk startup; there is no input file processing requirement.

State and persistence: it reads host command output and prints a report to stdout. No files are modified.

Dependencies and integration points: developer support script for diagnosing build environment minimums. Depends on many optional commands being in PATH and on GNU-ish awk/system behavior.

Risks: version regex is intentionally broad and can pick a non-version number from unusual output. Missing tools are silently omitted. Command execution from awk means PATH should be trusted.

Test signals: run on minimal and full development hosts, compare emitted versions against expected tool versions, and verify no hard failure when optional tools are missing.
