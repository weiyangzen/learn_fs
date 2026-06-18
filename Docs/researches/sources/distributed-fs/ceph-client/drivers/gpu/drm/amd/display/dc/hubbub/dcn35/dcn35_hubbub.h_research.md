# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.h

## Purpose

`dcn35_hubbub.h` defines the DCN3.5 Hubbub register and mask/shift list and declares DCN3.5 helper functions. It extends DCN3.2 with DCHVM/RIOMMU fields, Z8 self-refresh watermarks, host VM QoS thresholds, fine-grain clock gating, and DCN3.5 init/readback helpers.

## Important APIs, Types, And Functions

- `HUBBUB_REG_LIST_DCN35(id)` enumerates DCHUBBUB watermarks, VM aperture/fault registers, DET/compbuf, USR/UCLK/FCLK registers, SDPIF/clock/memory power, DCHVM/HVM registers, Z8 watermarks, and QoS force.
- `HUBBUB_MASK_SH_LIST_DCN35(mask_sh)` inherits DCN3.2 fields and adds HVM, compbuf, fine-grain clock gating, Z8 watermarks, legacy cstate/deepsleep, host VM QoS commit threshold, and DF min outstanding commit threshold fields.
- Declared functions include `hubbub35_construct`, `hubbub35_wm_read_state`, `hubbub35_get_dchub_ref_freq`, `hubbub35_program_watermarks`, `hubbub35_init_watermarks`, `dcn35_program_compbuf_size`, `dcn35_init_crb`, `hubbub35_init`, and `dcn35_dchvm_init`.

## Control Flow

The header supplies register metadata and prototypes only. Runtime flow is in `dcn35_hubbub.c`, where `hubbub35_construct` installs a DCN3.5 function table and the declared helpers are invoked during init, bandwidth programming, readback, and DCHVM setup.

## State And Persistence Behavior

The header owns no state. Its fields enable runtime mutation of watermark caches, DET/compbuf caches, global timer state, DCHVM state, QoS thresholds, and clock gating through the C implementation.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h`, inheriting DCN3.2 field coverage and helper prototypes. It integrates with ASIC register-table generation, DCN3.5 resource construction, DML watermark paths, DCHVM host-VM init, and debug clock-gating policy.

## Risks And Edge Cases

- `HUBBUB_REG_LIST_DCN35` contains repeated compbuf/debug/clock register entries, which may be accepted by table-generation macros but is a maintenance hazard.
- The header exposes HVM fields and DCHVM init prototype even though RIOMMU activity is runtime-dependent.
- Z8 fields must remain consistent with `hubbub35_wm_read_state` and `hubbub35_program_stutter_z8_watermarks`.

## Test Signals

Build tests validate macro expansion and function prototypes. Runtime tests should verify Z8 watermark write/read, DCHVM init, QoS threshold programming, fine-grain clock gating, compbuf config-error checks, and inherited DCN3.2 watermark/DCC behavior.
