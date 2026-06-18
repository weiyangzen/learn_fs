# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.c

Purpose: generates firmware-like instruction words for the STI AWG block in data-enable mode, based on display timing parameters.

Important APIs and types: exported `sti_awg_generate_code_data_enable_mode()` fills `struct awg_code_generation_params` using `struct awg_timing`. Internal `enum opcode` names instruction types. `awg_generate_instr()` encodes opcode, argument, mux select, and data-enable bit into 14-bit RAM words, splitting long skip/repeat/replay counts across multiple instructions up to `AWG_MAX_ARG`. `awg_generate_line_signal()` builds one line's data-enable waveform.

Control flow: caller supplies a RAM buffer and zeroed/initial offset. Generation optionally emits trailing-line replay, emits active-line line signal plus replay loops in chunks of `AWG_MAX_ARG`, and optionally emits blanking-line replay. Line generation handles trailing pixels, active pixels, and blanking pixels with `SET`/`RPLSET`/`SKIP` instructions and an `AWG_DELAY` adjustment.

State and persistence: state is the caller-provided `ram_code` array and `instruction_offset`. Hardware programming is not done here; this file only generates code.

Dependencies and integration: depends on DRM logging and `sti_awg_utils.h`. It is linked into the STI DRM composite driver and likely consumed by VTG/HDMI/DVO timing code.

Risks: return values are OR-aggregated, so the first negative error remains negative but multiple errors are not distinguished. Instruction overflow is checked against `AWG_MAX_INST`; callers must provide a buffer of that size. The `while (arg_tmp > 0)` logic can return early for zero/negative skip cases and mutates `opcode` from SKIP to SET for one-pixel skips, so edge timings need careful tests.

Test signals: unit-level generation for zero/one/large trailing, active, and blanking intervals; instruction count overflow; and expected RAM opcodes for known display timings.
