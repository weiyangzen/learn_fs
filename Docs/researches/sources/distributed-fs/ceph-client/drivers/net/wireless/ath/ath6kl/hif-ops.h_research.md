# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif-ops.h

## Purpose
`hif-ops.h` is the inline dispatch layer for host interface operations. It wraps `ar->hif_ops` function pointers with consistent names and optional HIF debug logging, hiding whether the actual bus is SDIO, USB, or another implementation.

## Important APIs, types, and functions
The wrappers cover synchronous read/write (`hif_read_write_sync()`), asynchronous writes (`hif_write_async()`), IRQ enable/disable, scatter request get/add/enable/submit/cleanup, suspend/resume, diagnostic read/write, BMI read/write, power on/off, stop, pipe send, default pipe lookup, service-to-pipe mapping, and free pipe queue depth. These wrappers are the call surface consumed by HIF common code, HTC mailbox code, HTC pipe code, BMI, diagnostics, and core power management.

## Control flow and integration
All wrappers immediately dispatch through `ar->hif_ops`. Mailbox code uses read/write and scatter calls for SDIO mailbox traffic; pipe HTC uses pipe wrappers for USB-style message flow; diagnostics use `diag_read32`/`diag_write32`; firmware boot uses BMI calls; suspend and resume pass through cfg80211 WOW parameters. Because the wrappers do not null-check `ar->hif_ops` or individual callbacks, core initialization must attach a complete HIF ops table before these APIs are called.

## State and persistence behavior
This header owns no state. It is a stateless dispatch layer over the persistent `struct ath6kl` bus binding. The effects of calls persist in lower bus driver queues, device power state, interrupts, scatter pools, and firmware/target state.

## Dependencies and integration points
It includes `hif.h` for structures and `debug.h` for logging. This creates a simple but performance-sensitive inline layer used throughout ath6kl. Pipe-specific wrappers assume HIF implementations provide pipe primitives; mailbox paths rely on read/write/scatter primitives.

## Risks and test signals
Risks include missing bus callbacks, calling wrappers before HIF attach or after cleanup, and mismatched assumptions about synchronous versus asynchronous completion context. Test signals include boot over each supported HIF type, suspend/resume/WOW cycles, BMI firmware download, diagnostic reads, scatter transfer enable/fallback, and pipe send completions under backpressure.
