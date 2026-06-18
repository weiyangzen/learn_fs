# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/mutexes.c

## Purpose
This POSIX implementation supplies the global `libhdfs` mutexes and lock wrappers using pthreads.

## Important APIs, Control Flow, and State
`jclassInitMutex` uses `PTHREAD_MUTEX_INITIALIZER`. `jvmMutex` is initialized by an ELF constructor function: it initializes `jvmMutexAttr`, sets it to `PTHREAD_MUTEX_RECURSIVE`, and initializes `jvmMutex`. `mutexLock` and `mutexUnlock` call `pthread_mutex_lock` and `pthread_mutex_unlock`, printing errors to stderr and returning the pthread error code.

## Dependencies and Integration Points
It depends on pthreads and `os/mutexes.h`. The recursive JVM mutex matters because JVM/bootstrap paths can re-enter helper code that also needs synchronized TLS or cached-class work.

## Risks and Test Signals
Constructor ordering is the main platform risk; all users assume the mutexes are ready before first libhdfs call. There is no destructor for `jvmMutexAttr`. Tests should compile on supported Unix linkers, verify recursive lock behavior, check concurrent JVM bootstrap, and fail builds where constructor attributes are unavailable.
