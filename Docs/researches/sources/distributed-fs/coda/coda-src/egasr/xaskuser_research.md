# sources/distributed-fs/coda/coda-src/egasr/xaskuser

## Purpose
Tk/Wish UI script that asks the user how to repair an inconsistent file: remove it, use a replica, or use another file.

## APIs, Types, and Functions
Defines Tcl procedures `mkbuttons`, `GetIncResp`, `getreplicas`, `makeentries`, `getentries`, `oklistboxcommand`, and `repairwithnamedfile`. It invokes external `filerepair` and uses Tk widgets including radiobuttons, entry, listbox, scrollbar, canvas, and buttons.

## Control Flow, State, and Persistence
The script receives directory and filename, constructs `oname`, lists children under the conflict expansion, and displays replica metadata from `ls -l`. On OK it exits with codes: `0` no action/cancel, `1` remove, `2` repaired from selected replica, `3` repaired from named file. For replica or named-file repair it runs `filerepair` before exit.

## Dependencies and Integration
Depends on Wish/Tk, shell execution, `filerepair`, and the expanded repair directory layout created by `cfs beginrepair`. It is launched by `xfrepair`.

## Risks and Test Signals
Risks include command execution without robust error reporting, path/list handling with whitespace, reliance on X display, old Tk `pack append` syntax, and hidden `filerepair` failures due to `catch`. Test signals are correct exit code, visible replica list, successful `filerepair` invocation, and integration with `xfrepair` cleanup.
