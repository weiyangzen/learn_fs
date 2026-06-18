# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_cts.h

Purpose: public interface for DisplayPort compliance test support.

Important APIs/types/functions: declares `dp_handle_automated_test()`, `dp_set_test_pattern()`, `dp_set_preferred_link_settings()`, and `dp_set_preferred_training_settings()`. Includes `link_service.h` for `dc_link`, `dc`, link settings, training overrides, and DP test-pattern types.

Control flow and integration: protocol and HPD/test handling code can include this header to respond to DP CTS DPCD requests or user/debug preferred-link overrides.

State and persistence: no header state. Declared functions mutate `dc_link` state and hardware/DPCD state in the C implementation.

Dependencies, risks, and test signals: API changes affect DP compliance, link training, and debug override callers. Build coverage plus DP CTS runtime testing validate this contract.
