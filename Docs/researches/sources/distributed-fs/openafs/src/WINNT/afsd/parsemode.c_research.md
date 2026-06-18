# sources/distributed-fs/openafs/src/WINNT/afsd/parsemode.c

Purpose: parses symbolic Unix chmod-style mode expressions into an updated mode bitmask for OpenAFS Windows command tooling.

Important APIs/types/functions: `parsemode(char *symbolic, afs_uint32 oldmode)` supports `u`, `g`, `o`, `a` selectors; `+`, `-`, and `=` actions; permission symbols `r`, `w`, `x`, `X`, `s`, and `t`; and comma-separated clauses. It uses mode groups from `parsemode.h` and `S_ISDIR` from stat macros. Invalid syntax reports through `fs_Die(EINVAL, "invalid mode")` and exits.

Control flow: starts from `oldmode & ALL_MODES`, parses a `who` mask, requires an action, accumulates a permission mask, then applies the action. If `who` is omitted, additions respect a hard-coded umask `022`; `=` with no `who` clears all tracked bits before adding masked bits. `X` only adds execute bits when the old mode is a directory or already has execute bits.

State/persistence: no state or persistence. It returns a computed mode value and terminates the process on invalid input.

Dependencies/integration: includes `parsemode.h` and `fs.h` for constants and `fs_Die`. Used by chmod-like AFS command code.

Risks: invalid input exits the whole process instead of returning an error. The hard-coded umask `022` ignores process/user umask. Fallthrough from `=` to `+` is intentional but not annotated. The parser handles symbolic modes only; numeric parsing must occur elsewhere.

Test signals: cover each selector/action/symbol, comma-separated operations, `X` for directories and executable files, setuid/setgid/sticky bits, omitted `who` with umask behavior, and invalid syntax exits.
