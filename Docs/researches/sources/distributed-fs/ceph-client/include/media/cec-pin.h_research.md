# sources/distributed-fs/ceph-client/include/media/cec-pin.h

Purpose: Provides the low-level bit-banging CEC pin framework interface for hardware that controls the HDMI CEC line directly instead of using a full CEC controller.

Important APIs/types/functions: `struct cec_pin_ops` supplies `read`, `low`, `high`, optional IRQ enable/disable, free/status, HPD/5V reads, and optional high-level `received` handling. `cec_pin_changed` reports interrupt-observed pin state changes. `cec_pin_allocate_adapter` creates a CEC adapter with monitor-all and monitor-pin capabilities added.

Control flow: A driver allocates a pin adapter, implements electrical line control callbacks, and calls `cec_pin_changed` from IRQ context when voltage changes. The core timing engine drives low/high transitions and decodes received bits.

State and persistence: Pin state is stored in `struct cec_adapter` and its optional `struct cec_pin`, not in this header. The ops table must remain valid for adapter lifetime.

Dependencies and integration: Depends on `media/cec.h` and integrates GPIO-like HDMI CEC implementations with the normal CEC character-device/core stack.

Risks and test signals: Risks are timing jitter, sleeping in IRQ path, incorrect open-drain high behavior, and stale ops lifetime. Test bit timing, arbitration, HPD/5V event propagation, IRQ and polling modes, and adapter delete cleanup.
