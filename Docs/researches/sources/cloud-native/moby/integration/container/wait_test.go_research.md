# sources/cloud-native/moby/integration/container/wait_test.go

Purpose: integration coverage for `ContainerWait`, including already-exited containers, blocking waits, explicit wait conditions, auto-remove, and restart-triggered exits.

Important APIs and helpers: `TestWaitNonBlocked`, `TestWaitBlocked`, `TestWaitConditions`, and `TestWaitRestartedContainer` use `client.ContainerWaitOptions`, `WaitConditionNotRunning`, `WaitConditionNextExit`, `WaitConditionRemoved`, `ContainerAttach`, `ContainerStop`, `ContainerRestart`, and internal container state polling.

Control flow: non-blocked cases run containers that have already exited and ensure wait returns the recorded status. Blocked Linux cases start a signal-trapping loop, issue stop, and require wait to unblock with the trapped exit code. Condition cases attach stdin to hold the process, start waiting, verify no premature result while running, then send a newline and assert exit code. Restart cases wait on a running process, call restart with SIGTERM, and require the wait to complete on the pre-restart exit.

State and persistence: the tests exercise daemon wait channels over container state transitions: running, exited, removed, and restarted. Auto-remove mode validates wait with removal condition when the container disappears after exit.

Dependencies and integration: depends on request client creation, busybox shell behavior, attach streams, daemon event/state propagation, Windows capability differences, and poll helpers.

Risks: signal handling and sub-second sleeps are Linux-specific in some paths. Race sensitivity is visible in comments disabling parallelism for wait-condition tests. Windows cannot catch SIGTERM in the same way.

Test signals: provides strong behavioral signal for wait result delivery, absence of premature notifications, exit-code propagation, and wait behavior across restart and removal conditions.
