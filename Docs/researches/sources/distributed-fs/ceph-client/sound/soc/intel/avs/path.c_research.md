# sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.c

Purpose: Instantiates topology path templates into live DSP pipelines/modules/bindings, configures module-specific IPC payloads, manages conditional paths, and drives path state transitions.

Important APIs/functions: Public lifecycle/state functions are `avs_path_create()`, `avs_path_free()`, `avs_path_bind()`, `avs_path_unbind()`, `avs_path_reset()`, `avs_path_pause()`, `avs_path_run()`, and `avs_path_set_constraint()`. Runtime control helpers `avs_peakvol_set_volume()` and `avs_peakvol_set_mute()` bridge ALSA controls to firmware parameters. Internal module creators cover copier, WHM, peakvol/gain, mux, micsel, up/down mixer, SRC/ASRC, AEC, WoV, probe, base, and generic extended modules.

Control flow: Creation matches FE/BE hardware params to a topology variant, serializes with `path_mutex` and `comp_list_mutex`, creates pipelines, creates modules through GUID dispatch, sends initial configs, resolves bindings, arms internal bindings, appends the path to `adev->path_list`, then discovers conditional paths. Run/pause/reset walk pipelines in firmware-safe order and maintain `path->state`.

State and persistence: Live state is `struct avs_path` with pipeline/module/binding lists, conditional source/sink links, DMA ID, and current firmware state. Module instance IDs and gateway attributes are stored per module. Lists are protected by `path_mutex`, `comp_list_mutex`, and `path_list_lock` depending on scope.

Dependencies and integration: Consumes parsed topology structures, ACPI NHLT blobs, ALSA PCM params, firmware IPC helpers, module ID utilities, AVS controls, and platform attributes such as `ALTHDA`.

Risks: Error unwinding spans firmware-created pipelines/modules and driver lists. The local snapshot has duplicated lines in `avs_append_dma_cfg()` and duplicate `spin_lock()` in `avs_path_free_unlocked()`, both serious build/deadlock signals. Conditional path matching uses topology names/IDs and can fail silently if topology components are not registered in order. NHLT/default blob size and DWORD alignment are firmware-sensitive.

Test signals: DPCM playback/capture path create/free, all module GUID creator paths, conditional AEC reference paths, NHLT lookup failure/fallback, bind/unbind ordering, repeated trigger state transitions, and lockdep with concurrent FE/BE opens.
