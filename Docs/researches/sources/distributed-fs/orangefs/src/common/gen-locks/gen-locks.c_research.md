# sources/distributed-fs/orangefs/src/common/gen-locks/gen-locks.c

Purpose: Implements POSIX-backed generic mutex and condition-variable wrappers for OrangeFS.

Important APIs/functions: Mutex functions initialize normal, recursive, and process-shared pthread mutexes; lock, unlock, trylock, destroy, and return `pthread_self()`. Condition functions initialize normal/shared pthread conditions, wait/timedwait, signal, broadcast, and destroy.

Control flow: Thin wrappers forward to pthread APIs, adding null-pointer validation for destroy paths and attribute setup for recursive/process-shared initialization.

State/persistence: No module global state. All state lives in caller-provided pthread mutex/condition objects.

Dependencies/integration: Included through `gen-locks.h`, which maps portable `gen_*` macros to these POSIX functions when `__GEN_POSIX_LOCKING__` is selected. Used by common infrastructure such as gossip and id-generator.

Risks: Checks `pthread_*attr_*` return values with `rc < 0`, but pthread APIs return positive errno-style values; failures may be missed. If `gen_posix_shared_cond_init()` fails after creating a local attr, it can return without destroying it. Return semantics are mixed between pthread positive error codes and documented `-errno` comments.

Test signals: Build/run with normal, recursive, process-shared locks, timed waits, and failure injection for attr setup.
