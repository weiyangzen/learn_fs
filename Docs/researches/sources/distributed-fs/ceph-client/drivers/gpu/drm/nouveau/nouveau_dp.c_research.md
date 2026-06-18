
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dp.c

## Purpose
Implements DisplayPort probing, capability discovery, link training, HPD IRQ service, and mode validation for Nouveau encoders. It supports SST, optional MST, LTTPR probing, eDP fixed-rate tables, sink count handling, and downstream bandwidth limits.

## Important APIs, Types, and Functions
The external functions are `nouveau_dp_detect()`, `nouveau_dp_train()`, `nouveau_dp_power_down()`, `nouveau_dp_link_check()`, `nouveau_dp_irq()`, and `nv50_dp_mode_valid()`. Internal helpers include `nouveau_dp_probe_dpcd()`, `nouveau_dp_probe_lttpr()`, `nouveau_dp_has_sink_count()`, `nouveau_dp_train_link()`, and `nouveau_dp_link_check_locked()`. Module parameter `mst` controls whether MST capability is used.

## Control Flow
Detection powers the AUX path, serializes on `outp->dp.hpd_irq_lock`, handles eDP cached status, asks NVIF for physical detect status, reads DPCD and LTTPR capabilities, clamps lanes and rates by DCB and repeater limits, programs supported rates through `nvif_outp_dp_rates()`, reads DP descriptor/downstream info, and decides between disconnected, SST, or MST. If MST is active, detection delegates topology setup to `nv50_mstm_detect()`.

Training computes a minimum link rate from MST maximum link capacity or SST mode clock/bpc, then tries decreasing lane counts and advertised rates until `nvif_outp_dp_train()` succeeds. Certain sinks require post-link-training adjustment loops using DPCD link status and `nvif_outp_dp_drive()`. IRQ handling services MST topology or CEC/sink-count changes and then reports HPD events through `nouveau_connector_hpd()`. Mode validation compares mode bandwidth against cached link capacity and DP downstream dotclock.

## State and Persistence
Persistent per-encoder DP state lives in `struct nouveau_encoder`: DPCD bytes, LTTPR caps/count, sorted link rates, lane count, max bandwidth, sink descriptor, downstream ports, sink count, and current training settings. This state is protected for IRQ-sensitive paths by `hpd_irq_lock`.

## Dependencies and Integration Points
The file integrates with DRM DP helpers, DRM MST helpers through `nv50_mstm_*`, NVIF output methods (`nvif_outp_detect`, AUX power, rates, train, drive), connector HPD handling, and encoder/connector state from Nouveau display code.

## Risks and Test Signals
Risks include incorrect AUX power state on GSP-managed disconnected ports, MST state races during suspend, malformed DPCD/rate arrays, LTTPR corner cases, and retraining loops that hide persistent link failures. Test signals include DP/eDP hotplug, MST hub plug/unplug, sink-count dongles, LTTPR repeaters, high-bpc HDR mode lists, suspend/resume with MST active, link loss IRQ retraining, and mode validation against low-bandwidth adapters.
