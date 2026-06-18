<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvc-console.h -->
# sources/distributed-fs/ceph-client/include/xen/hvc-console.h

## Purpose
This header exposes Xen HVC console boot/runtime console hooks and raw console output helpers.

## Important APIs, Types, And Functions
- `xenboot_console` is the boot console instance.
- Under `CONFIG_HVC_XEN`, `xen_console_resume()`, `xen_raw_console_write()`, and `xen_raw_printk()` are available.
- Without HVC Xen support, all helpers are inline no-ops, with `xen_raw_printk()` preserving printf format checking.

## Control Flow
Console code can write raw strings or formatted messages to the Xen console and resume console state after suspend. Non-HVC builds compile away the calls.

## State And Persistence
Console state is maintained by HVC/Xen console implementation, not this header. The boot console object persists externally.

## Dependencies And Integration Points
It integrates with Linux console infrastructure, Xen console backend/hypercalls, suspend/resume, and early boot logging.

## Risks And Edge Cases
Raw console writes may be used in fragile early/error paths, so format validation and no-op stubs are important. Callers must not assume output happens when `CONFIG_HVC_XEN` is disabled.

## Test Signals
Signals include visible early Xen console output, raw printk formatting, resume restoring console operation, and clean builds/behavior with HVC Xen disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/hvc-console.h -->
