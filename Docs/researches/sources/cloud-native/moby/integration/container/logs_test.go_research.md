# sources/cloud-native/moby/integration/container/logs_test.go

Purpose: Validates container log retrieval across log drivers, TTY/no-TTY stream handling, stdout/stderr selection, and empty-tail follow behavior.

Important APIs and flow: `TestLogsFollowTailEmpty` runs a sleeping container and ensures `ContainerLogs` with stdout and `Tail: "2"` can be copied without EOF error. `TestLogs` runs `testLogs` for local and json-file drivers. Each case runs a command writing stdout and stderr, waits for stop, calls `ContainerLogs`, and either copies raw TTY output or demultiplexes with `stdcopy.StdCopy`. Windows TTY output is normalized through `termtest.StripANSICommands` with a Server 2019 special case.

State and dependencies: Creates short-lived containers using selected log drivers. Depends on daemon logging backends, stream multiplex framing, and Windows console behavior.

Risks and signals: It catches log-driver regressions, incorrect TTY stream filtering, stdout/stderr mixups, and edge cases with empty log tails.
