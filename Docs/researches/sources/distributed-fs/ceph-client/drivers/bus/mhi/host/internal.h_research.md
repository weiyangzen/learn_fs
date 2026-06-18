# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/internal.h

## Purpose

`internal.h` is the private contract for the MHI host implementation. It centralizes protocol-derived constants, internal PM bit states, execution-environment helpers, ring/channel/event/cmd data structures, doorbell configuration, function prototypes, debugfs stubs, and inline helpers shared by `init.c`, `main.c`, `pm.c`, firmware-loading code, debugfs code, and transport glue.

## Important APIs, Types, And Functions

- Core structures: `struct mhi_ctxt`, `struct mhi_ring`, `struct mhi_cmd`, `struct mhi_buf_info`, `struct mhi_event`, `struct mhi_chan`, `struct db_cfg`, `struct state_transition`, and `struct mhi_pm_transitions`.
- State enumerations: `enum mhi_fw_load_type`, `enum mhi_ch_state_type`, `enum dev_st_transition`, `enum mhi_pm_state`, and `enum mhi_er_type`.
- State string lists: `MHI_EE_LIST`, `MHI_CH_STATE_TYPE_LIST`, `DEV_ST_TRANSITION_LIST`, and `MHI_PM_STATE_LIST`, which feed both runtime string tables and trace symbolic output.
- Access predicates: `MHI_REG_ACCESS_VALID()`, `MHI_PM_IN_ERROR_STATE()`, `MHI_PM_IN_FATAL_STATE()`, `MHI_DB_ACCESS_VALID()`, wake-doorbell validity checks, event-access checks, suspend-state checks, and fatal-error checks.
- Private prototypes expose MHI register access, event processing, channel preparation, power transitions, firmware loading, IRQ handlers, DMA mapping helpers, and device creation/destruction.

## Control Flow

The header does not execute logic directly beyond small helpers, but it defines the state model used by the rest of the host stack. PM state is represented as a single-bit mask rather than a dense enum value at runtime; transition functions use that bitmask and convert it to strings through `to_mhi_pm_state_str()`. The inline `mhi_is_active()` tests public MHI device state, while `mhi_trigger_resume()` raises a wakeup event and cycles transport runtime PM callbacks to force resume.

## State And Persistence Behavior

`struct mhi_ring` stores both coherent DMA addresses and host virtual pointers for ring base, read pointer, write pointer, doorbell address, and the device context write pointer. `struct mhi_chan` combines two rings, channel identity, direction, execution-environment mask, state, completion object, client callbacks, and locks. `struct mhi_event` owns event-ring state, tasklet dispatch, IRQ index, hardware/client/offload flags, and the function pointer that parses events. These structures persist for the lifetime of a registered controller, while per-channel ring memory is allocated when channels are prepared.

## Dependencies And Integration Points

`internal.h` includes `../common.h`, which supplies protocol register offsets, TRE encoders/decoders, public state lists, and MMIO field masks. It integrates with the Linux device model through the exported `mhi_bus_type`, with optional `CONFIG_MHI_BUS_DEBUG` implementations, and with tracepoints through common macro lists consumed by `trace.h`.

## Risks

The PM predicates assume `pm_state` remains a valid single-bit mask; any accidental multi-bit assignment can break string conversion, transition validation, and register access checks. Ring pointer fields are `void *` arithmetic in C extensions and must remain aligned to `struct mhi_ring_element`. Function pointer contracts are broad: missing controller callbacks are checked in `init.c`, but incorrect callbacks can invalidate all higher-level logic. Offload and hardware event flags change ownership of rings, so callers must honor them before allocation, IRQ request, processing, or teardown.

## Test Signals

Build coverage with tracepoints enabled and disabled, `CONFIG_MHI_BUS_DEBUG` enabled and disabled, and compilers that warn on enum/bitmask misuse is valuable. Runtime signals include valid symbolic trace output for PM, EE, channel command, and device transition states; no invalid PM strings during normal operation; and correct behavior for M2 doorbell policies configured through `db_access`.
