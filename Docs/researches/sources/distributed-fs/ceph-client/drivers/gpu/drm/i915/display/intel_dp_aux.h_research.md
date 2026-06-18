# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux.h

## Purpose

`intel_dp_aux.h` declares the small public interface for the i915 DP AUX transport implemented by `intel_dp_aux.c`. It is used by DP connector setup, register/power code, IRQ code, and higher-level DP logic that needs AUX initialization, cleanup, channel selection, packing helpers, or fast-wake sync timing.

## Important APIs

The header declares:

- `intel_dp_aux_init(struct intel_dp *intel_dp)`: initialize the DRM AUX object and platform-specific hardware callbacks.
- `intel_dp_aux_fini(struct intel_dp *intel_dp)`: release AUX lifetime resources.
- `intel_dp_aux_ch(struct intel_encoder *encoder)`: choose an AUX channel from VBT or platform defaults and reject duplicate claims.
- `intel_dp_aux_irq_handler(struct intel_display *display)`: wake AUX waiters from the display IRQ path.
- `intel_dp_aux_pack(const u8 *src, int src_bytes)`: pack up to four AUX payload bytes into a 32-bit register word.
- `intel_dp_aux_fw_sync_len(struct intel_dp *intel_dp)`: compute fast-wake AUX sync length, including quirk handling.

It forward declares `enum aux_ch`, `struct intel_display`, `struct intel_dp`, and `struct intel_encoder`, and includes `<linux/types.h>` for `u32` and fixed-width integer types.

## Control Flow And Integration

Typical setup flow is: encoder setup calls `intel_dp_aux_ch()` to choose `dig_port->aux_ch`; `intel_dp_init_connector()` calls `intel_dp_aux_init()` after default DP sink state is initialized; connector registration later registers the already initialized `drm_dp_aux`; IRQ setup calls `intel_dp_aux_irq_handler()` on AUX completion interrupts; encoder cleanup calls `intel_dp_aux_fini()`.

`intel_dp_aux_pack()` is exported because some DP paths or tests may need the same register packing format as the transfer implementation. `intel_dp_aux_fw_sync_len()` is exposed so other platform code can use the same fast-wake timing policy as AUX send-control programming.

## State And Persistence Behavior

The header has no state of its own. Its functions mutate `struct intel_dp` lifetime fields such as the DRM AUX object, AUX register callbacks, QoS request, and name allocation. Callers are expected to pair init/fini and ensure IRQ handler calls only target initialized display state.

## Dependencies And Risks

The API is tightly coupled to `struct intel_dp` and `struct intel_encoder` internals even though those structures are forward declared. Risks include init/fini imbalance, calling channel selection before encoder VBT/devdata is available, and using the pack helper with more than four bytes while assuming all bytes are included. The implementation clamps packing to four bytes, matching AUX data register width.

## Test Signals

Build coverage should catch missing type includes or signature drift. Runtime validation should show AUX devices registering/unregistering correctly, AUX IRQs waking transactions, DPCD/EDID reads succeeding after `intel_dp_aux_init()`, and no leaks or stale callbacks after `intel_dp_aux_fini()`.
