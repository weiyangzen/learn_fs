# sources/cloud-native/cri-o/test/hooks/checkhook.sh

## Purpose
Simple hook script that records hook invocation arguments and stdin.

## Important APIs, Types, And Functions
Shell script appends `$@` to `HOOKSCHECK`, reads one line from stdin, and appends that line too.

## Control Flow
Linear: echo args, read stdin, echo stdin.

## State And Persistence
Appends to the hook check file referenced by the `HOOKSCHECK` placeholder/environment used in tests.

## Dependencies And Integration Points
Executed through the OCI hooks mechanism configured by `checkhook.json`.

## Risks And Test Signals
The script assumes `HOOKSCHECK` is substituted or available. It reads only one stdin line, so multiline hook state is not captured.
