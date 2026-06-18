# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c

Purpose: Provides the DCN4.2 HPO DP link encoder variant. It reuses DCN31/DCN32 behavior and overrides state readback to match a three-stream/three-VC hardware shape.

Important APIs and functions: `dcn42_hpo_dp_link_enc_read_state` reads link enabled, lane count, mode, SAT VC0-VC2, and VC rate control 0-2. `hpo_dp_link_encoder42_construct` binds the DCN42 function table to a `dcn31_hpo_dp_link_encoder` object.

Control flow: function table entries mostly delegate to DCN31 implementations, with `is_in_alt_mode` using the DCN32 helper and `read_state` using the local reduced readback. Construction initializes context, instance, default HPD/transmitter unknowns, and register metadata.

State and persistence: same object state as DCN31/32. Hardware state is persistent in link encoder registers and read back on demand.

Dependencies and integration: includes DCN31/DCN32 link encoder headers, DCN42 header, register helpers, and stream encoder types. Integrated by DCN42 resource code.

Risks and test signals: inherited DCN31 allocation programming still writes four SAT rows, while DCN42 readback only reads three rows here; tests should confirm hardware supports or ignores the fourth row safely. Constructor and readback tests should validate DCN42 register tables and state arrays.
