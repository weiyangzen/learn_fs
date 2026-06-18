# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.h

Purpose: Declares the IPA microcontroller control and interrupt API used by IPA core setup, interrupt dispatch, power sequencing, and panic handling.

Important APIs and types: The header forward-declares `struct ipa` and declares `ipa_uc_interrupt_handler()`, `ipa_uc_config()`, `ipa_uc_deconfig()`, `ipa_uc_power()`, and `ipa_uc_panic_notifier()`. The public API intentionally exposes only lifecycle and notification hooks, not the shared-memory layout or command enums.

Control flow and integration: IPA core code calls config/deconfig around device setup and teardown, dispatches IPA microcontroller interrupt IDs through `ipa_uc_interrupt_handler()`, calls `ipa_uc_power()` when modem boot requires a proxy IPA power reference, and uses `ipa_uc_panic_notifier()` from crash-notifier handling.

State and persistence: The header has no state, but its functions mutate `ipa->uc_powered`, `ipa->uc_loaded`, runtime-PM references, interrupt enablement, and IPA retention state.

Dependencies: Requires the IPA core type and the `enum ipa_irq_id` definition to be visible before use. The implementation depends on IPA memory, interrupt, power, PM runtime, and register layers.

Risks: Misordered config/power/deconfig calls can leak or prematurely drop a runtime-PM reference. Missing enum visibility would break compilation. The API does not return status for config/deconfig/panic operations, so failures are logged internally.

Test signals: Compile coverage for interrupt dispatch and panic notifier users; runtime coverage for first-boot proxy power, IRQ enable/disable, and deconfig cleanup.
