# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/module.mk.in

## Purpose

This makefile fragment adds the Unix `bmi_tcp` transport sources to OrangeFS build source variables when `BUILD_BMI_TCP` is enabled. It also selects the epoll or poll socket collection backend.

## Important APIs, Types, And Functions

The file does not define C APIs. It manipulates build variables:

- `BUILD_BMI_TCP` gates the whole fragment.
- `BUILD_EPOLL = @BUILD_EPOLL@` receives configure-time substitution.
- `DIR := src/io/bmi/bmi_tcp` scopes paths.
- `LIBSRC`, `SERVERSRC`, and `LIBBMISRC` always receive `bmi-tcp.c` and `sockio.c`.
- When `BUILD_EPOLL` is set, all three source lists receive `socket-collection-epoll.c`, and `MODCFLAGS_$(DIR)/bmi-tcp.c` defines `__PVFS2_USE_EPOLL__`.
- Otherwise all three lists receive `socket-collection.c`.

## Control Flow

The conditional nesting is simple: if TCP BMI is not requested, no sources or flags are added. If TCP BMI is requested, common transport and socket I/O sources are added, then the socket collection backend is selected by `BUILD_EPOLL`.

## State And Persistence Behavior

The fragment only contributes make variables during the build. It has no runtime state and no generated persistent outputs of its own.

## Dependencies And Integration Points

It depends on the configure system replacing `@BUILD_EPOLL@` and the surrounding OrangeFS build using `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and per-file `MODCFLAGS_*`. It is the build-time integration point that keeps `bmi-tcp.c` synchronized with the correct socket collection header through `__PVFS2_USE_EPOLL__`.

## Risks And Edge Cases

- If `BUILD_EPOLL` substitution is non-empty when the platform cannot compile epoll headers or calls, the build selects the Linux epoll backend incorrectly.
- If the make dialect treats `ifdef BUILD_EPOLL` as true for an unexpected placeholder value, the epoll path may be selected accidentally.
- `MODCFLAGS_$(DIR)/bmi-tcp.c` only defines the switch for `bmi-tcp.c`; any other source that needs the same compile-time branch would need its own flag.

## Test Signals

Build tests should verify `BUILD_BMI_TCP` disabled, TCP with poll backend, and TCP with epoll backend. The generated compile command for `bmi-tcp.c` should include `-D__PVFS2_USE_EPOLL__` only for the epoll build, and link inputs should contain exactly one socket collection implementation.
