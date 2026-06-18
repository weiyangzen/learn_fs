<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c

Purpose: Ice Lake-specific DSP operations for firmware logging, debug-window slot lookup, D0ix policy, and a firmware-load workaround.

Important APIs, types, and functions: debugfs-only `avs_icl_enable_logs()`, packed debug-window slot descriptors, `avs_icl_log_buffer_offset()`, `avs_icl_d0ix_toggle()`, `avs_icl_set_d0ix()`, `avs_icl_load_basefw()`, and `avs_icl_dsp_ops`.

Control flow: log enabling builds a variable-sized `avs_icl_log_state_info` with priorities for selected resources and sends it by IPC. Log buffer offset reads MEMWND2 slot descriptors from debug SRAM and finds a slot whose type/resource matches debug log for the requested core. D0ix toggle requests full power for pipeline-running IPCs and for payload-carrying IPCs. Base firmware loading allocates a dummy HDA capture stream, temporarily raises VS_LTRP.GB to 95 us, starts the stream to avoid low-power link entry, calls the generic HDA basefw loader, then stops/cleans the stream and restores VS_LTRP.

State and persistence: no file-local persistent state. Firmware logging state is sent to firmware; VS_LTRP is saved and restored.

Dependencies and integration points: used by ICL/JSL specs in `core.c`; reuses CNL interrupt handling, APL log status/coredump, and HDA loader. Depends on MEMWND2 layout agreed with firmware.

Risks: debug-window packed structures must match firmware exactly. `avs_icl_enable_logs()` validates resource mask against `max_libs_count`; wrong firmware config can reject logging. Firmware load workaround must always release stream and restore LTRP on all exits.

Test signals: ICL firmware boots reliably with dummy capture workaround, debug log offsets resolve for active cores, D0ix transitions do not occur during running pipeline IPCs, and logging priorities reach firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/icl.c -->
