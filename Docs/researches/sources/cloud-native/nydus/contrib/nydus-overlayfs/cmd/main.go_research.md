# sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main.go

## Purpose
This Go command is a containerd mount helper that receives overlay mount arguments, strips Nydus/Kata passthrough metadata, converts known mount options to syscall flags, and invokes `mount(2)`.

## Important APIs, Types, and Functions
Key symbols are `mountArgs`, `parseArgs`, `parseOptions`, `run`, `main`, version variables `Version` and `BuildTime`, and injectable `mountFn`. Constants identify filtered options: `extraoption=` and `io.katacontainers.volume=`.

## Control Flow
`main` builds a urfave CLI app and requires exactly four positional arguments. `run` calls `parseArgs`, logs the parsed mount, calls `parseOptions`, and invokes `mountFn(fsType, target, fsType, flags, data)`. `parseArgs` validates overlay filesystem type, non-empty target, expects `-o`, splits comma options, and filters containerd/Kata metadata. `parseOptions` maps known options to Linux mount flags and passes unknown options as comma-joined mount data.

## State, Persistence, and Dependencies
There is no durable state. The process performs a privileged mount syscall. Dependencies include `urfave/cli`, `pkg/errors`, `golang.org/x/sys/unix`, `syscall`, and logging.

## Integration Points
It integrates with containerd `fuse.mount` style invocation and Kata container volume metadata. `mountFn` is intentionally injectable for tests.

## Risks and Test Signals
The flags table appears counterintuitive for positive options such as `dev`, `exec`, `suid`, and `rw`, mapping them to disabling flags (`MS_NODEV`, `MS_NOEXEC`, `MS_NOSUID`, `MS_RDONLY`). This may be deliberate inverse handling or a bug. Parsing assumes at least four args; CLI `Before` enforces that for real runs, but direct calls to `parseArgs` with short slices would panic. Tests cover filtering, validation, flag/data splitting, run success, and error wrapping.
