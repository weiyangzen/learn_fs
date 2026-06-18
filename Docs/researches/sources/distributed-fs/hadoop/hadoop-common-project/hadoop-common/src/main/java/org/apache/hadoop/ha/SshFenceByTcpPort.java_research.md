# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/SshFenceByTcpPort.java

Purpose: Built-in SSH fencer that connects to the target host and kills the process listening on the HA service TCP port using `fuser`; if killing is indeterminate, it verifies the port with `nc`.

Important APIs and types: `SshFenceByTcpPort extends Configured implements FenceMethod`, with `checkArgs()`, `tryFence()`, `createSession()`, `doFence()`, `execCommand()`, nested `Args`, and nested JSch `LogAdapter`. Config keys are `dfs.ha.fencing.ssh.connect-timeout` and `dfs.ha.fencing.ssh.private-key-files`.

Control flow: Arguments parse optional user and SSH port. `tryFence()` creates a JSch session with configured private keys and disabled strict host-key checking, connects with timeout, then executes `fuser -v -k -n tcp <port>`. Exit code 0 succeeds. Exit code 1 triggers `nc -z host port`; if the port is closed, fencing is considered successful.

State and persistence: No Java persistence. External side effects include SSH authentication and remote process termination. JSch logger is globally set.

Dependencies and integration points: Used via `NodeFencer` alias `sshfence`. Depends on JSch, remote `fuser`, remote `nc`, SSH keys, service address, and `StreamPumper`.

Risks: `StrictHostKeyChecking=no` trades security for operability. Lack of root permissions can make `fuser` indeterminate. Remote command availability and PATH are platform-specific. `nc` behavior varies by implementation. Hostname resolution and SSH user defaults matter.

Test signals: `TestSshFenceByTcpPort` covers argument parsing, configured host/port/key behavior, and command outcome paths; integration testing requires an SSH-capable environment.
