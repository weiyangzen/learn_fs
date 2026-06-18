# sources/distributed-fs/ceph-client/scripts/check-function-names.sh

## Purpose
`check-function-names.sh` rejects object files containing function names that conflict with section-name conventions used by `-ffunction-sections`.

## APIs, Types, And Functions
It uses `${NM:-nm}`, `awk`, and `grep -E` to find text/weak symbols named `startup`, `exit`, `split`, `unlikely`, `hot`, or `unknown`, with optional suffix after a dot.

## Control Flow
The script validates it received an existing object file, extracts candidate symbols, prints one error per bad symbol, and exits nonzero if any are found.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
It depends on nm output format and kbuild object-file checking. It integrates with linker script assumptions around text section names.

## Risks And Test Signals
Risks include false positives for intentionally named local functions and missed symbols if nm output changes. Test signals are nonzero exit with clear diagnostics for an object defining `startup()` and zero for normal objects.
