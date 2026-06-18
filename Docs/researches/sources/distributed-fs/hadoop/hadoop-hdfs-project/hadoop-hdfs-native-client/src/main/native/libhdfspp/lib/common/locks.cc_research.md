<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc

## Purpose
Implements lock abstractions used by libhdfspp, especially the globally configurable GSSAPI mutex required to serialize non-thread-safe security library calls.

## Important APIs, Types, And Functions
`LockGuard` locks a `Mutex*` in its constructor and unlocks in its destructor. `DefaultMutex` wraps `std::mutex`. Static `LockManager` state includes default test and GSSAPI mutexes, `_state_lock`, and `_finalized`. `InitLocks`, `getGssapiMutex`, `TEST_get_default_mutex`, and `TEST_reset_manager` manage global lock state.

## Control Flow
Clients call `LockManager::InitLocks` once to replace the GSSAPI mutex before use. After finalization, subsequent init attempts fail. `getGssapiMutex` returns the active mutex under state lock; `LockGuard` then applies RAII locking to it.

## State And Persistence
State is process-global pointers to mutex implementations plus finalization flag. It is not durable and test reset can reopen initialization.

## Dependencies And Integration Points
Depends on `hdfspp/locks.h` and C++ mutexes. Security/authentication code should use `getGssapiMutex` around GSSAPI calls.

## Risks
`InitLocks` stores a raw pointer and leaves lifetime management to the caller. `TEST_reset_manager` is not protected by `_state_lock`, so it is only safe in isolated tests. Swapping lock proxies after use is explicitly risky.

## Test Signals
Tests should cover null mutex rejection in `LockGuard`, one-shot initialization, failed second initialization, custom mutex use, default reset in tests, and concurrent `getGssapiMutex` access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc -->
