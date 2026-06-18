# sources/cloud-native/moby/integration/container/kill_test.go

Purpose: Tests container kill API signal validation, state transitions, restart-policy interactions, user handling, and OOMKilled inspect flags.

Important APIs and flow: `TestKillContainerInvalidSignal` sends invalid signals and asserts errors without changing running state. `TestKillContainer` covers default kill, non-killing signal, and SIGTERM. `TestKillWithStopSignalAndRestartPolicies` checks whether a kill matching `StopSignal` disables restart while a different signal allows restart policy behavior. Additional tests cover killing stopped containers, killing containers running as another user, and inspect `State.OOMKilled` after memory exhaustion.

State and dependencies: Uses running containers, restart policies, cgroup memory/swap limits, and inspect state. It skips Windows or unsupported cgroup conditions where behavior differs.

Risks and signals: It catches invalid signal validation, incorrect restart suppression, inability to signal non-root-user containers, and incorrect OOM state reporting.
