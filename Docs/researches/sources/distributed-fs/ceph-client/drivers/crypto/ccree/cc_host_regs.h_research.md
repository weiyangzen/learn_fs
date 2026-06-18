# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_host_regs.h

## Purpose

`cc_host_regs.h` is a generated register-offset and bitfield map for CryptoCell host-facing registers. It supplies symbolic offsets and field widths for interrupt handling, security/fuse status, boot capability discovery, version/signature reads, power-down control, host SRAM access, and component identification.

## Important APIs, Types, And Functions

The file defines macros only. Important groups include `CC_HOST_IRR_*` interrupt raw-status bits, `CC_HOST_IMR_*` interrupt mask bits, `CC_HOST_ICR_*` interrupt clear bits, `CC_HOST_SEP_SRAM_THRESHOLD_*`, `CC_HOST_SIGNATURE_*`, `CC_HOST_BOOT_*` hardware capability bits, `CC_HOST_VERSION_*`, key-valid registers, `CC_HOST_POWER_DOWN_EN_*`, input-pin removal bits, peripheral/component ID registers, and host SRAM data/address/ready registers.

## Control Flow

There is no control flow in this header. Runtime code combines these macros through `CC_REG(...)`, `cc_ioread()`, `cc_iowrite()`, and bit helpers. The request manager uses host interrupt bits for completion and CPP abort classification. Power management writes `HOST_POWER_DOWN_EN`. SRAM manager uses `HOST_SEP_SRAM_THRESHOLD` on older revisions.

## State And Persistence Behavior

The represented state is hardware MMIO state. Interrupt status and clear bits are transient. Boot/version/security bits describe hardware configuration. Power-down state persists in the device until runtime PM resume disables it. SRAM data registers expose volatile device SRAM access.

## Dependencies And Integration Points

This header is consumed by `cc_driver.c`, `cc_request_mgr.c`, `cc_pm.c`, `cc_sram_mgr.c`, debugfs, and FIPS/security handling. It must match the CryptoCell hardware revision layout, including the different signature/version offsets used by 630 and 712-class devices.

## Risks And Edge Cases

Wrong bit shifts can cause missed interrupts, failure to clear completion conditions, incorrect feature discovery, or unsafe power transitions. Host interrupt masks include both AES and SM abort bits by slot; request completion error reporting depends on these values matching hardware. The SRAM threshold must be word-aligned before the SRAM allocator trusts it.

## Test Signals

Boot logs should show correct hardware revision detection, no stuck interrupts, and successful request completions. Runtime PM suspend/resume should toggle power-down without losing later operation. Debugfs or register dumps can validate expected signature/version and interrupt-mask behavior on supported hardware.
