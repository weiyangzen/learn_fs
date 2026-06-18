# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_8b_10b.h

Purpose: public interface for the 8b/10b DP link-training implementation. It defines retry limits and exposes the complete training sequence plus the individually callable CR/EQ phases.

Important APIs/types: `LINK_TRAINING_MAX_CR_RETRY` caps total CR attempts at 100; `LINK_TRAINING_MAX_RETRY_COUNT` caps repeated unchanged training requests at 5. Exports `dp_perform_8b_10b_link_training`, `perform_8b_10b_clock_recovery_sequence`, `perform_8b_10b_channel_equalization_sequence`, `dp_decide_8b_10b_lttpr_mode`, and `decide_8b_10b_training_settings`.

Control flow and integration: consumers include the core DP training path and vendor retimer path. The phase exports let alternate training implementations reuse the standard CR/EQ algorithms while surrounding them with custom setup.

State/persistence: no storage of its own; all state is supplied through `dc_link`, `link_resource`, `dc_link_settings`, and mutable `link_training_settings`.

Dependencies: includes `link_dp_training.h`, so callers must use the common DP training structures and result enums.

Risks: changing retry constants changes interop behavior for marginal sinks and MST hubs. Since CR/EQ phase functions are exported, their assumptions about initialized `lt_settings` must stay documented and stable.

Test signals: compile coverage of all callers, standard 8b/10b training success/failure, and retimer code that reuses the phase APIs.
