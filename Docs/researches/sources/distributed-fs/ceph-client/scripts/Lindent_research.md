# sources/distributed-fs/ceph-client/scripts/Lindent

## Purpose
`Lindent` is a shell wrapper around GNU `indent` that applies Linux-kernel-style formatting options.

## APIs, Types, And Functions
It defines a `PARAM` string of indent options, parses `indent --version`, extracts major/minor/patch fields, conditionally appends `-il0` for indent versions at least 2.2.10, and finally executes `indent $PARAM "$@"`.

## Control Flow
The script exits if no version is detected. It then compares version components using shell arithmetic and runs `indent` with calculated options against all passed files.

## State And Persistence
It mutates files passed to `indent`; no separate state is stored. Formatting changes are persistent in the working tree.

## Dependencies And Integration Points
It depends on GNU indent output format and POSIX shell utilities. It integrates with kernel developer workflows for mechanical source formatting.

## Risks And Test Signals
Risks include non-GNU indent formats, unquoted numeric comparisons on unexpected versions, and broad in-place formatting churn. Test signals are a zero exit code on valid C files and expected kernel indentation changes.
