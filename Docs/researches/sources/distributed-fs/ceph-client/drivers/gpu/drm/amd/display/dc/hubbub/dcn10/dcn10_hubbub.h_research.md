# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.h

Purpose: Defines the common hubbub register schema and DCN1 concrete hubbub object. Later generations extend this header's register and field lists.

Important APIs and types: `struct dcn_hubbub_registers` is a large register address table spanning DCN1 through newer fields. `struct dcn_hubbub_shift` and `struct dcn_hubbub_mask` aggregate field metadata macros. `struct dcn10_hubbub` embeds `struct hubbub`, register tables, debug pstate index, and cached watermarks. Macros define register lists for common, VM, SR watermark, DCN10, HVM, retention, DCN32, DCN35, DCN4.01, and DCN4.2 fields. Function declarations expose watermark, DCHUB, reset, timer, and aperture helpers.

Control flow: resource code expands generation-specific register macros into static tables. Constructors bind those tables to a concrete hubbub object and install a `hubbub_funcs` vtable.

State and persistence: the struct tracks cached software watermark values to enforce safe lowering and exposes register metadata for persistent hardware programming.

Dependencies and integration: includes `core_types.h` and `dchubbub.h`. It is included by DCN20/21/30 and later generation hubbub headers.

Risks and test signals: because the register struct accumulates fields across generations, shifts/masks must remain consistent with generation-specific register lists. Compile-time resource table generation plus runtime readback tests are the best signals.
