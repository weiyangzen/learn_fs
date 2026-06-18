# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_uc.c

Purpose: Handles the minimal AP-side interface to the IPA-resident microcontroller: shared-memory layout, microcontroller interrupt dispatch, proxy power retention during firmware start, and panic notification.

Important APIs and functions: Public functions are `ipa_uc_interrupt_handler()`, `ipa_uc_config()`, `ipa_uc_deconfig()`, `ipa_uc_power()`, and `ipa_uc_panic_notifier()`. Internal pieces include `struct ipa_uc_mem_area`, command/response/event enums, `ipa_uc_shared()` for locating the `IPA_MEM_UC_SHARED` block, event/response interrupt handlers, and `send_uc_command()` for writing a command then raising the `IPA_IRQ_UC` register bit.

Control flow: Configuration clears `ipa->uc_powered`/`ipa->uc_loaded` and enables the two microcontroller IRQs. `ipa_uc_power()` takes a one-time runtime-PM proxy reference before the modem first boots the microcontroller. On `IPA_IRQ_UC_1`, `ipa_uc_response_hdlr()` accepts `INIT_COMPLETED`, marks the microcontroller loaded, enables IPA power retention, drops the autosuspend reference, and clears `uc_powered`; other responses are warnings. On `IPA_IRQ_UC_0`, event handling logs errors and ignores LOG_INFO. During panic, the AP sends `ERR_FATAL` and delays briefly to allow microcontroller state save.

State and persistence: Runtime state is held in `ipa->uc_powered`, `ipa->uc_loaded`, IPA power-retention state, and a function-static `already` flag that ensures only the first modem boot takes a proxy reference. The shared memory block is hardware-visible IPA SRAM; reserved bytes must not be touched. No durable storage is used.

Dependencies and integration points: Depends on IPA memory descriptors, IPA interrupt enable/disable routing, runtime PM, IPA power retention, register descriptors, MMIO accessors, and panic-notifier integration. It assumes the shared memory interface version is compatible with hardware interface `0x2000`.

Risks: The static `already` flag is process-wide, so reset/reprobe behavior depends on driver lifetime assumptions. Reserved shared-memory fields must remain untouched. Unexpected INIT responses can leave power references unchanged. Panic notification only runs when `uc_loaded` is true, so early crashes do not notify the microcontroller. Command writes need little-endian conversion and correct IRQ register bits.

Test signals: Confirm first modem boot keeps runtime PM active until `INIT_COMPLETED`; verify autosuspend reference is dropped exactly once; inject unsupported event/response values; test config/deconfig ordering with and without loaded firmware; validate panic notifier writes `ERR_FATAL` and delays; check suspend/resume or reset paths for stale `uc_powered`/`uc_loaded`.
