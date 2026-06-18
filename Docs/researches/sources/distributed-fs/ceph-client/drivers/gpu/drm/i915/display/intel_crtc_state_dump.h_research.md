# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc_state_dump.h

Purpose: public interface for CRTC state dumping and output-format name formatting. It forward-declares `struct intel_crtc_state`, `struct intel_atomic_state`, and `enum intel_output_format` to avoid pulling full display state definitions into callers.

Important APIs: `intel_crtc_state_dump(const struct intel_crtc_state *crtc_state, struct intel_atomic_state *state, const char *context)` logs a complete KMS diagnostic snapshot for one CRTC state, optionally including plane states from an atomic state. `intel_output_format_name(enum intel_output_format format)` returns a stable printable name or `"invalid"`.

Control flow and state: the header has no runtime behavior and no persistent state. It only exposes functions implemented in `intel_crtc_state_dump.c`.

Dependencies and integration: included by modeset setup, modeset verification, display commit/failure paths, DP code, and debugfs code that needs diagnostic output without depending on the implementation details.

Risks: the closing include guard comment names `__INTEL_CRTC_STATE_H__` while the guard macro is `__INTEL_CRTC_STATE_DUMP_H__`; this is cosmetic but can confuse readers. If `enum intel_output_format` changes, the implementation table must be updated to keep the API useful.

Test signals: compile coverage from all include sites is the main check. Functional validation comes from KMS debug logs that call the exported dump function.
