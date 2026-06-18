# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.h

## Purpose
`link_dp_irq_handler.h` declares the DP HPD RX IRQ and link-loss handling API used by link detection, training verification, and hotplug/event paths.

## Important APIs
- `dp_parse_link_loss_status()` evaluates IRQ lane/status data for link loss.
- `dp_should_allow_hpd_rx_irq()` gates handling based on link state, branch status, or bandwidth allocation.
- `dp_handle_link_loss()` performs DPMS off/on recovery.
- `dp_read_hpd_rx_irq_data()` reads and normalizes DPCD IRQ status into `union hpd_irq_data`.
- `dp_handle_hpd_rx_irq()` performs top-level short-pulse handling and reports detection/link-loss/deferred-work outcomes.

## Control Flow And Integration
The header is included by capability verification for post-training IRQ reads and by hotplug handling code for runtime short-pulse processing. It depends only on `link_service.h`.

## State, Risks, And Test Signals
The API mutates `dc_link` runtime state and returns multiple signals through booleans and output pointers. Tests should compile all call sites and exercise link-loss parsing, IRQ data reads for DPCD revisions, deferred handling, and USB4/branch allow-gate behavior.
