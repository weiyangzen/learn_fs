# sources/cloud-native/containerd/pkg/imageverifier/bindir/processes_windows.go

Purpose: Windows process-management shim for verifier binaries. It places each verifier in a Windows Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, so closing the job tears down the verifier process tree.

Important APIs/types/functions: `process` stores the `exec.Cmd`, job handle, and opened process handle. `startProcess` creates a job object, sets extended limit information, starts the command, opens the verifier process with query/quota/terminate rights, assigns it to the job, and returns the wrapper. `cleanup` closes both handles and logs close failures.

Control flow: job object creation precedes `cmd.Start`; after start, `OpenProcess` obtains a handle suitable for `AssignProcessToJobObject`. Any setup failure after job creation calls `cleanup` before returning an annotated error.

State/persistence: runtime-only Windows kernel handles. No filesystem or metadata persistence.

Dependencies/integration: used by `bindir.runVerifier` on Windows. Depends on `golang.org/x/sys/windows` and containerd log context. The implementation is the Windows counterpart to Unix process-group cleanup.

Risks: one failure path after `OpenProcess` failure returns without calling `cleanup`, so the already-started process/job handle path should be reviewed carefully. Job assignment can fail when nested job restrictions apply. Handle leaks or failed job closure can leave verifier descendants running.

Test signals: indirectly exercised by the bindir slow-child timeout test on Windows; coverage should assert no lingering child and no handle cleanup errors.
