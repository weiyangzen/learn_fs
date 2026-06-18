# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_errno.h

## Purpose
Defines architectural TDX SEAMCALL status values and operand IDs consumed by the TDX implementation.

## Important APIs, Types, And Functions
`TDX_SEAMCALL_STATUS_MASK` extracts the high status field from RAX. Status constants include non-recoverable vCPU/TD failures, resumable interruption, invalid operand, operand busy, previous TLB epoch busy, incorrect page metadata, vCPU not associated, key errors, cache writeback completion, flush-vp-not-done, EPT walk failure, EPT entry state errors, and unreadable metadata fields. Operand IDs identify RCX, TDR, SEPT, and TD epoch.

## Control Flow
`tdx.c` masks SEAMCALL returns to detect operand-busy retry paths, invalid user operands, non-recoverable TD states, interrupted cache writeback, missing HKID cache work, and VP association races. The low 32-bit operand IDs are returned to userspace in selected hardware error cases.

## State And Persistence
No state is stored. The constants are stable ABI glue between TDX module returns and KVM error handling.

## Dependencies And Integration Points
Included by `tdx.h` and used throughout `tdx.c` in `TDX_BUG_ON` checks, retry decisions, teardown, and ioctl `hw_error` reporting.

## Risks
Incorrect status constants would route fatal module errors into retry paths or user errors into KVM BUG paths. Masking only high status bits means low operand details must be preserved when reporting `hw_error`.

## Test Signals
Fault-injection or mocked SEAMCALL tests for operand-busy, invalid operand, non-recoverable returns, cache writeback statuses, and metadata read failures validate usage.
