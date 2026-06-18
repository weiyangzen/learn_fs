# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.h

Purpose: exposes the modeset verification hooks used after atomic commits or when checking disabled state.

Important APIs: `intel_modeset_verify_crtc(struct intel_atomic_state *state, struct intel_crtc *crtc)` verifies active/changed CRTC state against hardware, while `intel_modeset_verify_disabled(struct intel_atomic_state *state)` validates disabled encoders/connectors/DPLLs.

Control flow/state: no local state. The interface deliberately accepts the full Intel atomic state because verification needs old/new connector state and CRTC-specific new state.

Dependencies/integration: included by commit tail or display verification paths; forward declarations avoid pulling in full atomic/CRTC definitions.

Risks/test signals: build failures or missing prototypes are the key header-level risk. Runtime validation belongs to the `.c` implementation.
