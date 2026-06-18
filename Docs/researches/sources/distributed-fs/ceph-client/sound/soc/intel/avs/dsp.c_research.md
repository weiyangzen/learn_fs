<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c

Purpose: common DSP core power/reset/stall helpers plus runtime module and pipeline instance lifecycle for AVS firmware paths.

Important APIs, types, and functions: core ops `avs_dsp_core_power/reset/stall/enable/disable()`, module lifecycle `avs_dsp_init_module()` and `avs_dsp_delete_module()`, pipeline lifecycle `avs_dsp_create_pipeline()` and `avs_dsp_delete_pipeline()`, private core reference helpers.

Control flow: core power/reset/stall update ADSPCS bits and poll matching acknowledge bits, with tracepoints and hardware propagation delays. Enabling a core powers it, exits reset, and unstalls; disabling stalls, resets, and powers down. Non-main DSP cores are reference-counted: first get disables D0ix then powers and sets D0, last put deletes D0 and re-enables D0ix. Module init allocates an instance ID, finds module metadata, gets the target core, loads module code if it is the first instance of an unloaded loadable module, sends IPC init-instance, and returns instance ID. Delete optionally sends delete-instance, frees ID, unloads module code when last instance goes away, and puts the core. Pipeline creation/deletion wrap firmware IPC with an IDA-backed pipeline ID.

State and persistence: `adev->core_refs`, module IDAs, pipeline IDA, and firmware module load state are persistent driver state. Module code may be loaded into DSP memory while at least one instance exists.

Dependencies and integration points: depends on platform DSP ops, IPC wrappers, module info from `utils.c/messages.c`, firmware transfer ops from `loader.c`, D0ix management in `ipc.c`, and path construction code.

Risks: error path in `avs_dsp_init_module()` after `avs_dsp_get_core()` but before successful IPC can jump to `err_mod_entry` without putting the core for some failures before `err_ipc`, so changes need close audit. Core ref underflow is not guarded in put. Firmware load/unload decisions rely on module IDA emptiness and module metadata accuracy.

Test signals: tracepoints show expected ADSPCS transitions, creating/deleting pipelines frees IDs, loadable module binaries transfer only for first instance and unload after last, and D0ix is disabled while secondary cores are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/dsp.c -->
