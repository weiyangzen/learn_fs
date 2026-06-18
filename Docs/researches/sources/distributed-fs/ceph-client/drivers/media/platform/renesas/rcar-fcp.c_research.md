# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-fcp.c

## Purpose
`rcar-fcp.c` is a small shared platform driver for Renesas Frame Compression Processor instances used by other media/display blocks. It does not expose a userspace node; it registers FCP devices in a global in-kernel list and exports helper APIs for other drivers to acquire a device reference, runtime-enable the block, and issue a soft reset.

## Important APIs, Types, And Functions
`struct rcar_fcp_device` stores the global list node, `struct device *`, and MMIO base. Exported APIs are `rcar_fcp_get()`, `rcar_fcp_put()`, `rcar_fcp_get_device()`, `rcar_fcp_enable()`, `rcar_fcp_disable()`, and `rcar_fcp_soft_reset()`. Probe/remove maintain `fcp_devices` under `fcp_lock`. `rcar_fcp_soft_reset()` writes `RCAR_FCP_REG_RST_SOFTRST` and polls `RCAR_FCP_REG_STA_ACT` clear with `readl_poll_timeout()`.

## Control Flow
Probe allocates and maps one FCP instance, sets maximum DMA segment size to `UINT_MAX`, enables runtime PM, appends the device to the global list, and stores drvdata. Consumers later call `rcar_fcp_get(np)`, which searches by DT node and returns a referenced device or `-EPROBE_DEFER` if not registered. Enable/disable are thin wrappers over runtime PM reference counting. Remove deletes the list entry and disables runtime PM.

## State And Persistence
State is limited to the process-lifetime global device list and runtime PM reference count. The driver writes only FCP reset/status registers. There is no userspace state, persistent config, or long-lived buffer ownership.

## Dependencies And Integration Points
The file depends on platform resources, OF matching for `renesas,fcpf` and `renesas,fcpv`, runtime PM, DMA mapping configuration, and exported media header declarations from `<media/rcar-fcp.h>`. It is an integration service for other R-Car multimedia drivers that need an FCP memory path.

## Risks
The global singleton-style list requires consumers to handle `-EPROBE_DEFER`. Runtime PM references must be balanced by consumers. Soft reset assumes the status register's active bit clears within 100 microseconds; hardware stuck active produces an error. Since `rcar_fcp_put()` tolerates NULL, consumers may hide missing optional FCP usage if they fail to check `ERR_PTR` results correctly.

## Test Signals
Check probe for both compatible strings, deferred acquisition before probe, balanced enable/disable PM counts, successful soft reset polling, and consumer-driver behavior when `rcar_fcp_get()` returns `-EPROBE_DEFER`. Removal should delete list membership without dangling references for properly balanced consumers.
