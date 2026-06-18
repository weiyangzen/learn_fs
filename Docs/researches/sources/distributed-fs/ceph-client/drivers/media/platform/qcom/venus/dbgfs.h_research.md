# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.h

## Purpose
`dbgfs.h` declares the Venus debugfs lifecycle and provides a compile-time conditional fault-injection helper.

## Important APIs
- `venus_dbgfs_init()` and `venus_dbgfs_deinit()` declarations.
- Under `CONFIG_FAULT_INJECTION`, exports `venus_ssr_attr` and defines `venus_fault_inject_ssr()` as `should_fail(&venus_ssr_attr, 1)`.
- Without fault injection, `venus_fault_inject_ssr()` is a constant false inline.

## Control Flow And Integration
`core.c` calls the debugfs init/deinit functions and uses `venus_fault_inject_ssr()` in the threaded ISR to optionally call `hfi_core_trigger_ssr()`. The header hides the configuration difference from core code.

## State And Persistence
No state is owned by the header. Fault-injection state lives in the `fault_attr` object declared in `dbgfs.c`.

## Dependencies
Includes `linux/fault-inject.h` and forward-declares `struct venus_core`.

## Risks
- Fault injection is only compiled when configured; tests that expect SSR injection must account for the inline false stub.
- Header consumers must not access `venus_ssr_attr` unless `CONFIG_FAULT_INJECTION` is enabled.

## Test Signals
Build coverage with and without `CONFIG_FAULT_INJECTION` should compile. Runtime with fault injection should expose and honor the `fail_ssr` debugfs attribute.
