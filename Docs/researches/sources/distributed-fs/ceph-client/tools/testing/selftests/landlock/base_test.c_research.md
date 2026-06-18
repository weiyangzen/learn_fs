# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/base_test.c

## Purpose
`base_test.c` validates the basic user-space ABI behavior of Landlock syscalls. It focuses on argument validation, ABI/version query behavior, errata query behavior, ruleset file descriptor semantics, file descriptor transfer, and credential transfer paths.

## Important APIs, Types, And Functions
The test uses `landlock_create_ruleset()`, `landlock_add_rule()`, `landlock_restrict_self()`, `struct landlock_ruleset_attr`, `struct landlock_path_beneath_attr`, `LANDLOCK_CREATE_RULESET_VERSION`, `LANDLOCK_CREATE_RULESET_ERRATA`, `LANDLOCK_RULE_PATH_BENEATH`, filesystem access rights such as `LANDLOCK_ACCESS_FS_READ_FILE`, `READ_DIR`, and `EXECUTE`, and logging flags used with `landlock_restrict_self()`. It also uses `prctl(PR_SET_NO_NEW_PRIVS)`, `open()`/`openat()`, `socketpair()`, `send_fd()`/`recv_fd()` from `common.h`, libkeyutils syscalls through `__NR_keyctl`, and kselftest assertions.

## Control Flow
`inconsistent_attr` probes `landlock_create_ruleset()` copy and size validation, including too-small buffers, NULL pointers, page-sized buffers, and non-zero trailing bytes. `abi_version` expects ABI version 9 and checks that query mode rejects non-zero attr pointers/sizes and unknown flags. `errata` queries the errata bitmask and validates incompatible argument combinations. `create_ruleset_checks_ordering`, `add_rule_checks_ordering`, and `restrict_self_checks_ordering` assert the priority order of invalid flags, invalid FDs, invalid types, invalid attrs, permission failures, and valid calls. Additional tests check that arbitrary FDs and logging-flag combinations produce `EBADFD`, `EBADF`, `EINVAL`, or success as expected.

`ruleset_fd_io` verifies that Landlock ruleset FDs reject read/write with `EINVAL`. `ruleset_fd_transfer` sends a ruleset FD across a UNIX socket to a child, where it is enforced and denies opening `/` while allowing `/tmp`; the parent remains unrestricted. `cred_transfer` enforces a directory-read-denying ruleset, then uses `KEYCTL_SESSION_TO_PARENT` from a child to exercise a credential installation path that bypasses normal `cred_prepare` and must preserve Landlock restrictions via credential transfer handling.

## State, Persistence, And Dependencies
The test mutates process credentials through capability dropping, `no_new_privs`, Landlock domain enforcement, UNIX socket FD passing, and session keyring manipulation. It opens `/tmp`, `/`, and `/dev/null` but does not persist files. It requires a kernel exposing Landlock ABI 9 semantics for the hard-coded version assertion and supporting the errata flag, keyctl session operations, and kselftest capability setup.

## Integration Points
`base_test.c` is a foundational Landlock selftest used to catch syscall ABI regressions independent of higher-level filesystem policy tests. It depends on `common.h` for capability management and FD passing and on `wrappers.h` for Landlock syscall wrappers. It interacts with the kernel's Landlock LSM hooks, anonymous inode/ruleset FD operations, UNIX SCM_RIGHTS, and keyring credential-transfer paths.

## Risks
The hard-coded ABI version expectation must be updated when the Landlock ABI advances. Error-ordering tests are intentionally brittle and will fail if the kernel changes validation precedence, even if user-visible behavior remains broadly compatible. `cred_transfer` depends on keyring permissions and session-keyring behavior that can vary with kernel configuration. Tests that call `prctl(PR_SET_NO_NEW_PRIVS)` or enforce Landlock affect the current process for the remainder of that test, so ordering and fixture isolation matter.

## Test Signals
Important pass signals are exact errno matches for invalid calls, successful valid ruleset creation/add/enforcement, inherited restrictions after SCM_RIGHTS transfer and keyctl credential transfer, and unchanged parent access in the FD-transfer test. Failures indicate ABI version drift, validation-order regressions, ruleset FD operation bugs, or lost Landlock state during credential replacement.
