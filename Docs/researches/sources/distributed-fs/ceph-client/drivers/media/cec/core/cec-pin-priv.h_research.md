# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-pin-priv.h

Purpose: This internal header defines the software bit-banged CEC pin engine’s state enum, error-injection bit layout, event queue constants, `struct cec_pin`, and internal pin helper prototypes.

Important APIs, types, and functions: `call_pin_op()`/`call_void_pin_op()` safely invoke `struct cec_pin_ops` callbacks if the adapter is registered. `enum cec_pin_state` enumerates Off/Idle, TX wait/start/data/custom/low-drive states, RX start/data/ack/low-drive states, and IRQ-monitor state. Error-injection defines pack RX and TX modes in a 64-bit per-op mask plus argument indices. `struct cec_pin` carries adapter/ops/kthread/timer state, logical-address mask, monitor flags, TX/RX bit/message state, event ring buffers, overrun/error counters, custom pulse/glitch settings, and optional `error_inj` arrays. Prototypes expose `cec_pin_start_timer()` and error-injection helpers.

Control flow and state: The enum is consumed by `cec-pin.c`’s timer and kthread. The event ring (`CEC_NUM_PIN_EVENTS`) decouples hrtimer/IRQ pin updates from userspace event queueing. `work_irq_change` requests IRQ enable/disable transitions between hrtimer polling and interrupt mode.

State and persistence behavior: All fields are per-adapter volatile state. The structure tracks transient bus timing, queued work, diagnostics counters, and debug injection settings; nothing is persisted outside the adapter lifetime.

Dependencies and integration points: Depends on public `<media/cec-pin.h>`, Linux atomic/types, and the core adapter registration model. Platform drivers such as `cec-gpio` supply the low/high/read/IRQ/status ops that this structure wraps.

Risks and edge cases: The state enum and timing code must remain in sync with `states[]` in `cec-pin.c`; adding states without updating timing/status can break the hrtimer engine. The event ring is bounded and drops events with a flag, so monitor-pin users must handle loss. Error-injection bit offsets are ABI-like for debugfs parser/show and pin consumption.

Test signals: Compile with and without `CONFIG_CEC_PIN_ERROR_INJ`, run pin-backed adapter RX/TX, monitor-pin event overflow, IRQ-mode transitions, and debugfs status to ensure every state/counter remains coherent.
