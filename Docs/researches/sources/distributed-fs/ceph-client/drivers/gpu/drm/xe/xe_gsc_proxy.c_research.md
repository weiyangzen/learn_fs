# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.c

## Purpose
Implements the software proxy that relays GSC firmware messages to CSME through the MEI GSC proxy component. Platforms with integrated GSC cannot let GSC directly reach CSME, so Xe submits proxy packets to GSC, forwards payloads to MEI, and returns MEI replies to GSC until an end message is received.

## Important APIs, Types, and Functions
- Public APIs: `xe_gsc_proxy_init`, `xe_gsc_proxy_start`, `xe_gsc_proxy_request_handler`, `xe_gsc_proxy_irq_handler`, `xe_gsc_proxy_init_done`, and `xe_gsc_wait_for_proxy_init_done`.
- Component callbacks: `xe_gsc_proxy_component_bind` and `xe_gsc_proxy_component_unbind` connect Xe to the MEI component via `I915_COMPONENT_GSC_PROXY`.
- Message helpers: `proxy_send_to_gsc`, `proxy_send_to_csme`, `validate_proxy_header`, `emit_proxy_header`, and `proxy_query`.
- IRQ helpers manipulate HECI2 CSR bits using `gsc_proxy_irq_clear` and `gsc_proxy_irq_toggle`.

## Control Flow
- `xe_gsc_proxy_init` initializes the mutex, validates `CONFIG_INTEL_MEI_GSC_PROXY` and root-tile assumptions, allocates a 64 KiB channel split into 32 KiB GSC-to-host and host-to-GSC buffers, registers the component, and installs a devm cleanup action.
- `xe_gsc_proxy_start` enables HECI2 proxy interrupts, manually triggers the first request handler, verifies proxy-normal FWSTS state, and marks `proxy.started`.
- `xe_gsc_proxy_request_handler` waits up to 20 seconds for the MEI component to bind, clears a pending interrupt, and runs `proxy_query` under `proxy.mutex`.
- `proxy_query` loops: send query/reply to GSC, validate GSC proxy header, forward GSC payload to CSME, validate CSME response, rewrap it with a GSC HECI header, and stop when GSC returns a `PROXY_END` header.
- HECI2 interrupts queue `GSC_ACTION_SW_PROXY` on the GSC ordered workqueue for serialized handling.

## State and Persistence
- `gsc->proxy.component`, `component_added`, `started`, BO/map pointers, and CPU CSME buffers are owned by `struct xe_gsc`.
- `proxy.mutex` protects component binding and message exchanges; GSC action bits are protected by `gsc->lock`.
- Cleanup disables IRQs, flushes GSC worker completion, clears `started`, removes the component, and avoids registering late devm actions during module unload.

## Dependencies and Integration Points
- Depends on MEI proxy component ops `send` and `recv`, Xe BO/GGTT buffer management, GSC packet submission helpers, runtime PM, forcewake, and HECI2 MMIO registers.
- Started from GSC firmware load completion and invoked later by IRQ path in `xe_irq.c`.
- Shares the same ordered workqueue as firmware load to avoid concurrent proxy/GSC operations.

## Risks and Edge Cases
- Component bind races are handled by polling, but a missing component after timeout fails proxy init.
- Header validation is critical: wrong source/destination, oversized payload, status errors, invalid zero-length payloads, or tiny CSME replies are rejected.
- `proxy_send_to_gsc` checks only input buffer size against 32 KiB; output bounds depend on GSC header validation and caller-provided channel layout.
- Interrupts are disabled if startup fails; missed cleanup would leave HECI2 interrupt generation active.

## Test Signals
- Probe with MEI proxy enabled should reach `HECI1_FWSTS1_PROXY_STATE_NORMAL`.
- Fault injection or mock MEI failures should exercise send/recv errors and IRQ disable rollback.
- Debug logs under `CONFIG_DRM_XE_DEBUG_SRIOV`/driver debug can show proxy KLV/message failures; HECI2 IRQ handling should queue work only when component exists.
