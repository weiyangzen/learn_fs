<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c

Purpose: debug/probing machine driver exposing a compress capture DAI for AVS runtime data extraction.

Important APIs, types, and functions: platform driver `avs_probe_mb`; `avs_probe_mb_probe()`; `avs_create_dai_links()`.

Control flow: when debugfs is enabled, board selection registers `avs_probe_mb` and then `avs_register_probe_component()`. Probe creates one DAI link named `Compress Probe Capture` with CPU DAI `Probe Extraction CPU DAI`, dummy codec, platform set to the board device, and registers card "AVS PROBE".

State and persistence: no private state in the board driver. Probe stream state is owned by the AVS probe component/debug layer.

Dependencies and integration points: depends on `CONFIG_DEBUG_FS`, `SND_HWDEP`, probe component registration from `probes.c`, and compress operations used to extract data from firmware probes.

Risks: debug-only feature must not be registered when debugfs is off. A mismatch between CPU DAI name and probe component breaks compress capture binding.

Test signals: card "AVS PROBE" appears under debug builds, compress capture opens on the probe DAI, and `probe_points` debugfs control can connect extraction points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/probe.c -->
