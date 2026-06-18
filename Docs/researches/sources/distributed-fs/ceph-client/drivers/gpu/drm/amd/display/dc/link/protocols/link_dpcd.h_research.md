# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dpcd.h

Purpose: declares the common DPCD read/write wrappers used by link protocol code.

Important APIs: `core_link_read_dpcd(struct dc_link *, uint32_t address, uint8_t *data, uint32_t size)` and `core_link_write_dpcd(struct dc_link *, uint32_t address, const uint8_t *data, uint32_t size)` return `enum dc_status`.

Control flow/state: all behavior is implemented in the `.c` file; the header defines the dependency contract for callers that should use partition-aware DPCD access instead of raw helper calls.

Dependencies/integration: includes `link_service.h` and `dpcd_defs.h`. It is widely used by DP training, eDP panel control, and DPIA code.

Risks: consumers assume these calls handle partitioning and may pass ranges crossing repeater/FEC boundaries; bypassing this header risks spec-violating AUX transactions.

Test signals: compile coverage across link protocol modules and runtime DPCD transactions on sinks with LTTPRs.
