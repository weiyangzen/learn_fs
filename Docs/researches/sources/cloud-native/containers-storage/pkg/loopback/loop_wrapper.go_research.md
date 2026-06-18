# sources/cloud-native/containers-storage/pkg/loopback/loop_wrapper.go

Purpose: defines Go-side Linux loop ioctl ABI structures and constants.

Important APIs, types, and functions: `loopInfo64` and constants `LoopSetFd`, `LoopCtlGetFree`, `LoopGetStatus64`, `LoopSetStatus64`, `LoopClrFd`, `LoopSetCapacity`, `LoFlagsAutoClear`, `LoFlagsReadOnly`, `LoFlagsPartScan`, `LoKeySize`, and `LoNameSize`.

Control flow: no runtime control flow; this file maps `x/sys/unix` constants into package-local names and defines the struct used with unsafe ioctl calls.

State and persistence: no state itself, but its layout controls how kernel loop status is read and written by `ioctl.go`.

Dependencies and integration points: depends on `golang.org/x/sys/unix`. `attach_loopback.go`, `ioctl.go`, and `loopback.go` rely on these constants and fields.

Risks and edge cases: ABI mismatch would corrupt ioctl calls. Field names are unexported, so only package code can manipulate them.

Test signals: validated only through real Linux loopback operations; no compile-time ABI assertion is present.
