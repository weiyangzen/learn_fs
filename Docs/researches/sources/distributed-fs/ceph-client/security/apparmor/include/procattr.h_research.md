# sources/distributed-fs/ceph-client/security/apparmor/include/procattr.h

Purpose: declares the AppArmor `/proc/<pid>/attr/` and LSM self-attribute helpers.

Important APIs: `aa_getprocattr()` renders a label into a process attribute string with optional newline. `aa_setprocattr_changehat()` parses changehat/permhat requests from procattr writes.

Control flow and integration: `lsm.c` maps `current`, `prev`, and `exec` procattr/getselfattr requests to task labels, calls `aa_getprocattr()`, and dispatches setprocattr commands such as `changehat`, `permhat`, `changeprofile`, `stack`, and on-exec variants. `aa_setprocattr_changehat()` bridges user text commands into task context label transitions.

State and persistence: no state is stored in this header; state lives in `aa_task_ctx` (`previous`, `onexec`, token) and current credentials. Dependencies are AppArmor label rendering, domain transition code, and LSM procattr hooks.

Risks and test signals: parsing must reject unterminated or empty buffers and audit invalid commands. Changehat is token-sensitive, so tests should cover successful hat change, permission-only checks, restore failure, invalid command auditing, newline rendering, and concurrent reads of stale/replaced labels.
