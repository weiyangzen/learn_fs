# sources/distributed-fs/coda/coda-src/egasr/xfrepair

## Purpose
Shell wrapper for graphical file repair. It authenticates, starts Coda repair mode, delegates user choice to `xaskuser`, ends repair mode, and optionally removes inconsistent files.

## APIs, Types, and Functions
Uses external commands `ctokens`, `cfs`, `xaskuser`, and `removeinc`; shell utilities `dirname` and `basename`; and a trap to run `cfs endrepair`.

## Control Flow, State, and Persistence
The script requires one filename and a valid Coda token. It chooses `xaskuser` only when `$DISPLAY` is set, starts `cfs beginrepair`, rejects local/global conflicts that expose both `local` and `global`, runs the UI with errors tolerated, always calls `cfs endrepair`, then interprets UI exit codes. Removal invokes `removeinc`; replica/named-file repairs are already done by `xaskuser`.

## Dependencies and Integration
Integrates command-line Coda repair (`cfs`) with the Tk UI and C helpers from this directory.

## Risks and Test Signals
Risks include no non-X fallback, hard-coded command names, trap only for selected signals, path whitespace exposure, and comments typo around `xaskuer`. Test signals are begin/endrepair pairing, conflict-type rejection, correct handling of xaskuser exit codes, and token preflight failure when unauthenticated.
