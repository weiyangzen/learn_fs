# sources/cloud-native/moby/daemon/top_unix.go

## Purpose
`top_unix.go` implements `docker top` on non-Windows platforms by combining container task PIDs with host `ps` output.

## Important APIs, Types, And Functions
Helpers include `validatePSArgs`, `fieldsASCII`, `appendProcess2ProcList`, `hasPid`, `parsePSOutput`, and `psPidsArg`. `ContainerTop` obtains task PIDs, runs `ps`, parses output, and logs a top event.

## Control Flow
Default `psArgs` is `-ef`. Arguments are validated to disallow remapping non-`pid` columns to `PID`. The daemon obtains the running task, rejects restarting containers, reads task PIDs, runs `ps` with `-q<pids>`, retries without `-q` for incompatible options, extracts stderr on failures, parses rows with a PID column, and includes matching processes plus thread continuation lines with `PID` value `-`.

## State And Persistence
No durable state is changed except event emission.

## Dependencies And Integration Points
Depends on OS `ps`, containerd task PID listing, API top response types, daemon container lookup/state, lazy regex, and errdefs.

## Risks
Parsing `ps` output is locale/implementation sensitive. The file intentionally uses ASCII-only whitespace parsing to avoid Unicode column spoofing. Retrying without `-q` can process more output but filters by PID afterward.

## Test Signals
`top_unix_test.go` covers argument validation, ASCII whitespace behavior, missing PID column, and output parsing.
