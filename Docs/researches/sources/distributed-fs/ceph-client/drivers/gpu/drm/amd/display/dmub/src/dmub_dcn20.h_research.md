# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.h

## Purpose

`dmub_dcn20.h` declares the common DCN20-era DMUB register map and hardware operations. Later DCN generation headers include it when they reuse the common register layout and function prototypes.

## Important APIs, Types, And Functions

`DMUB_COMMON_REGS()` lists common DMCUB registers: control, memory/security control, inbox0/inbox1, outbox0/outbox1, REGION3 code windows CW0-CW7, REGION4/5, scratch registers, GPINT data-in, display pipe disable, DMUIF soft reset, framebuffer base/offset, interrupt acknowledge, timer, and fault address registers.

`DMCUB_INTERNAL_REGS()` is empty in this header but acts as an extension hook for generation-specific internal registers. `DMUB_COMMON_FIELDS()` lists field names used to generate shifts and masks for DMCUB enable/reset/traceport, memory spaces, security reset/unit/status, region top/enable fields, pipe enable support, DMUIF reset, framebuffer base/offset, and outbox interrupt ack.

The header defines `struct dmub_srv_common_reg_offset`, `struct dmub_srv_common_reg_shift`, `struct dmub_srv_common_reg_mask`, and `struct dmub_srv_common_regs`. `dmub_srv_dcn20_regs` is exported by `dmub_dcn20.c`.

It declares DCN20 hardware functions for reset, reset release, backdoor load, window setup, inbox/outbox setup and pointer access, support/init checks, GPINT access, boot options, panel-power sequencing skip, firmware boot status, cached inbox/trace-buffer policy, current timer reads, and diagnostic capture.

## Control Flow And Data Flow

This header supplies the static register/field lists that `dmub_dcn20.c` expands into offset, mask, and shift tables. Service code stores the resulting table in `dmub->regs`; `dmub_reg.h` macros use it to translate generic register names into MMIO accesses.

Function declarations define the operations that the service layer can place in `struct dmub_srv_hw_funcs`. Runtime flow is therefore indirect: `dmub_srv` calls function pointers, and DCN20 implementations perform register-level operations.

## State And Persistence Behavior

The header itself has no state. It defines the shape of persistent register-table objects and the API surface used to mutate DMUB hardware state in the implementation.

## Dependencies And Integration Points

It includes `../inc/dmub_cmd.h` for `union dmub_gpint_data_register`, firmware status/options, and DMUB address/window/region types that are defined in nearby service headers. It forward-declares `struct dmub_srv`. DCN21, DCN30, DCN301, DCN302, and DCN303 headers include this header to inherit the common register and function declarations.

## Risks And Edge Cases

Changing `DMUB_COMMON_REGS()` or `DMUB_COMMON_FIELDS()` affects every generation that uses `struct dmub_srv_common_regs`. A field missing from the list cannot be accessed through the common `REG_*` macros. A field added here must exist in all generated register headers for every common-generation user or builds will fail.

The declaration `dmub_dcn20_init` is present in this header, but the corresponding definition is not in the researched `dmub_dcn20.c` file. That may be supplied elsewhere or unused by this tree; it is a symbol-consistency point to check during build/link validation.

## Test Signals

Signals include successful compilation of every generation that includes this header, correct expansion of register tables for DCN20 and derivative generations, link success for declared functions that are referenced by function tables, and runtime register access sanity during DMUB reset, boot, mailbox setup, and diagnostics.
