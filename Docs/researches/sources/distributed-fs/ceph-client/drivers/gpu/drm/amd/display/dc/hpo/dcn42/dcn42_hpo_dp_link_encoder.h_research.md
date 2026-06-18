# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.h

Purpose: Declares the DCN4.2 HPO DP link encoder constructor.

Important APIs and types: `hpo_dp_link_encoder42_construct` takes a `dcn31_hpo_dp_link_encoder` object plus context, instance, and DCN31-format register/shift/mask tables. It intentionally reuses the DCN31 concrete type for DCN42 behavior.

Control flow: resource construction code includes this header after DCN31 definitions and calls the constructor to bind the DCN42 vtable.

State and persistence: no state is defined here beyond constructor contracts.

Dependencies and integration: includes `link_encoder.h`, but prototypes refer to DCN31 link encoder structs, so include ordering matters. Integrated by DCN42 HPO resource setup.

Risks and test signals: the trailing include-guard comment names DCN32, a minor maintenance hazard. Compile tests should catch missing DCN31 declarations; runtime tests should validate the DCN42 vtable selection.
