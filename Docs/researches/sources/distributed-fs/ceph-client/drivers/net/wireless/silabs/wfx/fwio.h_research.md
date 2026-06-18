# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.h

Purpose: Declares the firmware-device initialization entry point.

Important APIs and types: Exports `int wfx_init_device(struct wfx_dev *wdev)`.

Control flow and integration: Called by `wfx_probe()` after bottom-half registration and before polling for the firmware startup indication.

State and persistence: The implementation initializes chip registers, loads firmware, and fills `wdev->keyset`; the header itself owns no state.

Dependencies: Depends on `struct wfx_dev` from WFx private data.

Risks and test signals: Tests should cover callers handling negative errors and ensuring BH polling is active before waiting for firmware-ready indications.

Test signals: Source read size: 15 lines, 272 bytes.
