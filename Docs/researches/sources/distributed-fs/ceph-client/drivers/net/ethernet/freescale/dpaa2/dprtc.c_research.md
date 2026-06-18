# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dprtc.c

Purpose: Implements the DPAA2 DPRTC object API as thin wrappers around Management Complex commands. It opens and closes control sessions and manages the single DPRTC interrupt line's enable state, cause mask, pending status, and status clearing.

Important APIs and functions: `dprtc_open()` encodes `DPRTC_CMDID_OPEN`, passes a DPRTC object ID, sends the command, and extracts the returned token. `dprtc_close()` invalidates that control session. `dprtc_set_irq_enable()` and `dprtc_get_irq_enable()` control the whole interrupt. `dprtc_set_irq_mask()`/`dprtc_get_irq_mask()` configure which causes assert the interrupt. `dprtc_get_irq_status()` reads pending bits using the caller-supplied status filter, and `dprtc_clear_irq_status()` clears W1C bits.

Control flow: Every exported function builds a zeroed `struct fsl_mc_command`, fills the encoded header with command ID, flags, and token, casts `cmd.params` to the command-specific packed structure, writes parameters with CPU-to-little-endian conversions when needed, calls `mc_send_command()`, and decodes response fields on success. There is no retry, caching, locking, or asynchronous behavior.

State and persistence: The only local state is stack command storage. Persistent state is in the MC-managed DPRTC object: the open token, interrupt enable bit, interrupt mask, and pending event bits. After close, all later operations require a fresh token.

Dependencies and integration points: Uses `linux/fsl/mc.h`, `mc_encode_cmd_header()`, `mc_send_command()`, and `mc_cmd_hdr_read_token()`. It integrates with callers that know DPRTC event bits from `dprtc.h`, such as PPS and external timestamp events.

Risks: Callers must pass valid output pointers; the wrapper does not defensively check them. IRQ status read writes the input `*status` into the request, so uninitialized caller status can change firmware-side filtering semantics. ABI packing and command versions are inherited from `dprtc-cmd.h`.

Test signals: MC command success/error propagation, open/close token validity, IRQ mask get-after-set, event status read/clear behavior, and interrupt delivery under PPS/ETS events are the key runtime tests. Static tests should verify endian conversions and no unchecked command response use after errors.
