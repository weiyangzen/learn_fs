# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401/dcn401_hubbub.h

## Purpose

`dcn401_hubbub.h` declares the DCN4.01 Hubbub constants, field map, DCC helper APIs, segment programming APIs, arbiter API, and constructor. It shifts the interface toward DCN4 watermarks, address-v3 DCC, DML2 arbiter integration, and segment-based CRB programming.

## Important APIs, Types, And Functions

- Constants: `DCN4_01_CRB_SIZE_KB`, `DCN4_01_DEFAULT_DET_SIZE`, and `DCN4_01_CRB_SEGMENT_SIZE_KB`.
- `HUBBUB_MASK_SH_LIST_DCN4_01(mask_sh)` covers global timer, soft reset, self-refresh/p-state force, urgent A/B, SR A/B plus SR tiers 1-3, VM aperture, urgent flip/nom/MALL, refcycles to memory/meta, DET/compbuf, USR, UCLK/FCLK secondary watermarks, VM fault, SDPIF, memory power, timeout detection, ROB status, debug, and cstate swath check fields.
- Declared DCN4.01 APIs include watermark programming, address-v3 DCC support functions, two-plane DCC capability, `dcn401_program_arbiter`, `hubbub401_construct`, DET/compbuf segment programming, DET update waiting, and CRB init.

## Control Flow

The header has no executable control flow. Its field list enables `dcn401_hubbub.c` to build a function table and drive DCN4.01 register programming from DML2 and display init paths.

## State And Persistence Behavior

No state is stored in the header. The declared functions mutate cached Hubbub state and DCHUBBUB registers for DCN4.01 watermarks, DCC capability outputs, timeout/debug controls, DET/compbuf segment state, and VM behavior.

## Dependencies And Integration Points

It includes `dcn32/dcn32_hubbub.h` for inherited base types and helpers, and it introduces APIs used by DCN4.01 resource construction, DML2 display arbiter code, DCC plane validation, and HWSS resource programming.

## Risks And Edge Cases

- Header and implementation must agree on A/B-only DCN4.01 watermark coverage; C/D fields are not exposed here.
- Timeout and ROB status fields are hardware-debug-sensitive; accidental writes through a reused helper could affect diagnostics.
- Address-v3 DCC APIs have different swizzle enum and pixel-format signatures from older DCC helpers, so function-table selection must be correct.
- Segment units are not KiB in the public DET/compbuf segment functions; callers must convert before calling.

## Test Signals

Build coverage should validate every field macro. Runtime signals include DML2 arbiter writes, timeout threshold programming, ROB status handling, DCC capability for address-v3 swizzles, DET/compbuf segment apply, A/B watermark readback, and VM fault reporting.
