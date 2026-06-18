# sources/distributed-fs/ceph-client/rust/kernel/debugfs/file_ops.rs

## Purpose
`file_ops.rs` maps Rust debugfs traits to C `file_operations`. It provides operation tables for formatted reads through `seq_file`, text writes from user slices, binary reads and writes with offsets, and read-write combinations.

## Important APIs, Types, and Functions
`FileOps<T>` stores the C `file_operations`, Unix mode bits, and the invariant that inode private data points to a valid `T`. Traits `ReadFile`, `ReadWriteFile`, `WriteFile`, `BinaryReadFile`, `BinaryWriteFile`, and `BinaryReadWriteFile` provide const operation tables. Important callbacks include `writer_open`, `writer_act`, `write`, `write_only_open`, `write_only_write`, `blob_read`, and `blob_write`.

## Control Flow
Formatted files use `single_open` to create a `seq_file`; `writer_act` pulls the `T` pointer from `seq.private` and prints through `Writer`. Read-write text files add a `write` callback that retrieves the same private data from the `seq_file` and calls `Reader`. Write-only text files store the inode private pointer directly in `file.private_data`. Binary files use `simple_open`, then `blob_read` or `blob_write` calls the `BinaryWriter` or `BinaryReader` implementation with the user buffer and file offset.

## State and Persistence
The operation tables are static constants. Per-open state is managed by the kernel file and seq_file structures. No durable state exists; writes mutate the backing `T` through the trait implementation, usually via interior mutability.

## Dependencies and Integration Points
This file depends on `debugfs::traits`, `callback_adapters::Adapter`, `SeqFile`, `seq_print!`, `UserSlice`, `UserPtr`, and Linux file operation bindings. It is consumed by `Dir` and `ScopedDir` constructors to select file mode and callbacks.

## Risks
The main risks are raw-pointer type mismatches and offset handling. `FileOps::adapt` uses transmute, so adapter layout contracts must hold. Text writes ignore `ppos` and return the full input count on success. Binary operations must convert sizes to `isize` safely and report negative offsets or conversion failures correctly through errno.

## Test Signals
Read formatted files, write text files with valid and invalid inputs, exercise binary partial reads/writes at offsets, seek with `default_llseek`, and test all permission modes. Fault injection for invalid user buffers and large offsets should return errno without corrupting backing data.
