# sources/distributed-fs/ceph-client/kernel/elfcorehdr.c

## Purpose

`elfcorehdr.c` stores and parses the physical location and optional size of the ELF core header supplied to a kdump capture kernel. The values are used for vmcore handling and also by crash-dump detection paths such as `is_kdump_kernel()`.

## Important APIs, Types, And Functions

- `elfcorehdr_addr` is a globally exported `unsigned long long` initialized to `ELFCORE_ADDR_MAX`, meaning no core header is configured.
- `elfcorehdr_size` stores an optional parsed size.
- `setup_elfcorehdr()` parses the early boot parameter `elfcorehdr=[size[KMG]@]offset[KMG]` using `memparse()`.
- `early_param("elfcorehdr", setup_elfcorehdr)` registers the parser during early boot.

## Control Flow

When the kernel receives `elfcorehdr=`, `setup_elfcorehdr()` rejects a null argument, parses the first number into `elfcorehdr_addr`, and then checks for `@`. If present, the first number is reinterpreted as `elfcorehdr_size` and the value after `@` becomes the header physical address. The function succeeds when parsing advanced the input pointer and otherwise returns `-EINVAL`.

## State And Persistence Behavior

The parsed address and size are global kernel runtime state. They are set once during early boot and exported for other crash-dump code. There is no disk persistence.

## Dependencies And Integration Points

This file depends on `crash_dump.h`, `memparse()`, early boot parameter handling, and the kdump/vmcore subsystem. `elfcorehdr_addr` is exported with `EXPORT_SYMBOL_GPL` because other kernel code needs to detect and locate crash-dump metadata.

## Risks And Edge Cases

- An omitted argument returns `-EINVAL`.
- The parser accepts size plus address only when separated by `@`; otherwise the single parsed value is treated as the address.
- Incorrect bootloader-provided addresses or sizes can prevent vmcore discovery or mislead kdump detection.

## Test Signals

Test by booting capture kernels with `elfcorehdr=offset` and `elfcorehdr=size@offset`, checking `/proc/vmcore` availability where configured, validating `is_kdump_kernel()` behavior, and verifying invalid parameter handling in early boot logs.
