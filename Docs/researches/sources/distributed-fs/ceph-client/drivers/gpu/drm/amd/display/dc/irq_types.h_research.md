# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq_types.h

Purpose: central IRQ type and source enumeration for AMD display core.

Important APIs/types/functions: defines `interrupt_handler`, opaque `irq_handler_idx`, `DAL_INVALID_IRQ_HANDLER_IDX`, `enum dc_irq_source`, `enum irq_type`, `DAL_VALID_IRQ_SRC_NUM`, `DAL_PFLIP_IRQ_SRC_NUM`, interrupt context and polarity enums, `DC_DECODE_INTERRUPT_POLARITY`, `struct dc_timer_interrupt_params`, and `struct dc_interrupt_params`.

Control flow and integration: ASIC mappers return `enum dc_irq_source` values from hardware IDs; consumers use these stable enum values to register, enable, and acknowledge interrupts. `enum irq_type` aliases the first source in grouped ranges so callers can derive per-pipe IRQ sources by adding instance offsets.

State and persistence: no runtime state. The enum order is persistent ABI within the driver and is explicitly required to match the base driver.

Dependencies and risks: depends on `os_types.h` and forward-declares `dc_context`. The largest risk is reordering or inserting enum values incorrectly, which would desynchronize table indexes, base-driver expectations, and range arithmetic. Range macros assume contiguous PFLIP, VUPDATE, VBLANK, VLINE, and underflow values.

Test signals: compile coverage across all IRQ table initializers, assertions for `DAL_VALID_IRQ_SRC_NUM`, and runtime checks that each hardware source maps to the intended enum. Any enum change should trigger broad ASIC IRQ regression testing.
