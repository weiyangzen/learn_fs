<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h

## Purpose
Declares common utility APIs and small templates shared across libhdfspp networking, protobuf, callback, and synchronization code.

## Important APIs, Types, And Functions
The header defines `mutex_guard`, status/protobuf/base64/random/safe-disconnect/high-bit declarations, `lock_held`, `get_asio_socket_ptr` with a specialization for real TCP sockets, and `SwappableCallbackHolder<CallbackType>`.

## Control Flow
Most functions are implemented in `util.cc`. `SwappableCallbackHolder` enforces a one-time set, optional one-time swap before access, and one-time access pattern under a mutex, logging invariant violations.

## State And Persistence
Utility functions are stateless. `SwappableCallbackHolder` stores one callback and three boolean lifecycle flags.

## Dependencies And Integration Points
Used by async runtime, RPC, block reader, DataNode connection, and tests with mock sockets/callbacks.

## Risks
`lock_held` is only a heuristic and can perturb lock state if used incorrectly. `SwappableCallbackHolder::AtomicSwapCallback` can continue after invariant violations and still return/set values in some branches; callers must check the `swapped` flag. Callback retrieval returns copies and does not guard callback execution.

## Test Signals
Tests should cover socket pointer specialization, callback holder valid/invalid sequences, lock-held behavior, and declarations against implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h -->
