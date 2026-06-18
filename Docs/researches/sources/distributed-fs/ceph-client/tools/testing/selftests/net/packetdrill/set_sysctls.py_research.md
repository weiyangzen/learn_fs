# sources/distributed-fs/ceph-client/tools/testing/selftests/net/packetdrill/set_sysctls.py

## Purpose
`set_sysctls.py` is a packetdrill helper that changes proc/sysctl files and writes a restoration shell script for the packetdrill process.

## Important APIs and functions
- Reads `PACKETDRILL_PID` from the environment to name `/tmp/sysctl_restore_${PACKETDRILL_PID}.sh`.
- Iterates over command-line arguments of the form `<proc-file>=<val>`.
- Uses `subprocess.check_output(['cat', path])` to capture current values and writes `echo "old" > path` commands to the restore script.
- Uses `os.system('echo "new" > path')` to apply the requested value and then marks the restore script executable.

## Control flow
At import/execution time it opens the restore file, writes a bash shebang, processes all arguments in order, applies new values immediately, and chmods the restore script.

## State and persistence
It mutates proc files in the current namespace and persists a temporary restore script under `/tmp`. Packetdrill scripts can run that restore script at the end using their parent PID convention.

## Dependencies and integration points
It depends on Python 3, `PACKETDRILL_PID`, readable/writable proc files, `/tmp`, `cat`, shell redirection, and packetdrill scripts that know to call the restore file. It complements `defaults.sh` for per-test sysctl changes.

## Risks and edge cases
Arguments are split on every `=`, so values containing `=` are unsupported. `os.system` with interpolated paths/values assumes trusted packetdrill input. Missing `PACKETDRILL_PID` raises a KeyError before any friendly error. Restore scripts are left in `/tmp` if tests do not execute them or clean up.

## Test signals
The main signal is subsequent packetdrill behavior under modified sysctls. A restore script at `/tmp/sysctl_restore_${PACKETDRILL_PID}.sh` is evidence that previous values were captured.
