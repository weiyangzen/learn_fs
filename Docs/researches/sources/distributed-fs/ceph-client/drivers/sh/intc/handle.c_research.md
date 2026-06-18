# sources/distributed-fs/ceph-client/drivers/sh/intc/handle.c

Purpose: builds encoded INTC handles from platform hardware descriptor tables. Handles compactly encode register access function, mode, enable/disable register indexes, field width, and field shift.

Important APIs and functions: `intc_get_mask_handle`, `intc_get_prio_handle`, and `intc_get_sense_handle` find fields for an enum id, optionally falling back to group ids. `intc_set_ack_handle` stores per-IRQ ack handles and `intc_get_ack_handle` retrieves them. `intc_enable_disable_enum` applies force-enable/force-disable operations across all matching mask and priority entries before or after IRQ registration.

Control flow: the core calls these helpers during controller registration to select primary/secondary handles, populate priority/sense lists, and configure forced descriptor bits. At runtime chip code consumes the encoded handles through access dispatch tables.

State and dependencies: static `ack_handle[INTC_NR_IRQS]`; descriptor arrays for groups, mask regs, priority regs, sense regs, ack regs; register index table in `intc_desc_int`. Dependencies include handle macros and `intc_get_reg`. Risks are descriptor search state using register/field cursors, group fallback only one level deep, `BUG()` for invalid priority descriptors, and per-IRQ ack array bounds. Test signals are successful mapping of every platform enum id, warning-free registration, force-enable/disable register effects, and ack handling for controllers with pending-clear registers.
