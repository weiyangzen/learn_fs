# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_awg_utils.h

Purpose: public declarations for STI AWG instruction generation helpers.

Important APIs and types: defines `AWG_MAX_INST` as 64, `struct awg_code_generation_params` with output RAM pointer and instruction offset, `struct awg_timing` with total/active/blanking/trailing line and pixel counts plus blanking level, and `sti_awg_generate_code_data_enable_mode()`.

Control flow: callers populate timing and generation parameters, call the generator, then program generated RAM words elsewhere.

State and persistence: no storage in the header. The generated state is caller-owned through `ram_code` and `instruction_offset`.

Dependencies and integration: includes `linux/types.h`; implemented by `sti_awg_utils.c` and linked into `sti-drm.o`.

Risks: the API assumes `ram_code` points to at least `AWG_MAX_INST` 32-bit entries. `instruction_offset` is 8-bit, which is enough for 64 entries but should remain aligned with `AWG_MAX_INST`.

Test signals: compile users against this header and verify generator output stays under `AWG_MAX_INST` for supported display timings.
