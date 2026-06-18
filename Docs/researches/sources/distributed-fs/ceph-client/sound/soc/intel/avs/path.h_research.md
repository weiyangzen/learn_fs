# sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.h

Purpose: Declares the live AVS path object model and public path/control APIs used by PCM and control code.

Important APIs/types: `struct avs_path` owns path DMA ID, pipeline list, state, conditional path lists, source/sink pointers, topology template, owner device, and global list node. `struct avs_path_pipeline` stores firmware pipeline instance ID plus module/binding lists. `struct avs_path_module` stores firmware module ID/instance ID and gateway attributes. `struct avs_path_binding` stores resolved source/sink modules and pins. Public functions create/free paths, bind/unbind, reset/pause/run, set PCM constraints, and update peakvol controls.

Control flow role: PCM callbacks use this header to create paths in `hw_params`, prepare them to reset/pause, start them on trigger, and free them in `hw_free`/suspend. Control code can call peak volume/mute update helpers against live module objects.

State and persistence: Defines transient runtime state only. Topology pointers are borrowed and expected to outlive active paths.

Dependencies and integration: Includes `avs.h` and `topology.h`; depends on list heads, `avs_audio_format`/`avs_tplg_*` structures, and ALSA mixer control types.

Risks: Ownership is non-obvious because runtime structures hold borrowed topology pointers and firmware instance IDs. Incorrect list initialization or teardown can corrupt global path state. Conditional path fields share the same struct as normal paths, so code must distinguish spawned paths from standard PCM paths by context.

Test signals: Compile coverage for all users, KASAN/lockdep during repeated stream open/close, and control updates after path creation but before path free.
