# sources/distributed-fs/ipfs-kubo/core/commands/profile.go

## Purpose

`profile.go` implements the system profiling command that collects Go runtime and Kubo diagnostic profiles from a running daemon into a zip archive. It is used for debugging performance and operational issues.

## Important APIs, Types, and Functions

`sysProfileCmd` emits a streaming zip and a CLI `profileResult`. Options include output path, collector list, profile duration, mutex profile fraction, and block profile rate. It uses `profile.WriteProfiles`, `profile.Options`, `archive/zip`, and a Windows-safe timestamp format.

## Control Flow

The run function parses collector names and durations, reads mutex profile fraction, creates an `io.Pipe`, starts a goroutine that wraps the pipe writer in a zip writer and calls `profile.WriteProfiles`, then emits the pipe reader as octet-stream content type `application/zip`. The CLI post-run consumes the reader, chooses either the explicit output path or `ipfs-profile-<timestamp>.zip`, creates the file, copies archive bytes, and emits a text result with the output filename.

## State and Persistence Behavior

The command reads live daemon/runtime profiling state and writes a zip file only in CLI post-run. It does not persist repo data. Profiles may contain diagnostic metadata such as goroutine stacks, binary/version data, and allocation/mutex/block information.

## Dependencies and Integration Points

Dependencies include Kubo `profile` collectors, go-ipfs-cmds streaming, zip archive writing, and command error typing. It is `NoLocal`, targeting a running daemon's state.

## Risks and Test Signals

Risks include privacy-sensitive profile contents, long-running CPU/trace collection, pipe goroutine error propagation, archive close ordering, and output file overwrite behavior through `os.Create`. Tests should cover duration parsing, zero profile time, block profile rate parsing, collector list propagation, content type/encoding, CLI default filename format, explicit output path, copy errors, and zip readability.
