# sources/distributed-fs/ceph-client/sound/core/seq/seq.c

Purpose: main ALSA sequencer module entry point and module parameter owner.

Important APIs and state: defines `seq_client_load[]` autoload list, default timer module parameters (`seq_default_timer_class`, `seq_default_timer_sclass`, card/device/subdevice/resolution), module aliases for `/dev/snd/seq`, and init/exit functions `alsa_seq_init()` and `alsa_seq_exit()`.

Control flow: init clears client data, registers the sequencer character device, creates proc entries, creates the internal system client, and initializes autoload support. Exit tears down system client, proc entries, queues, device registration, and autoload in reverse order.

State and persistence: module parameters persist while the module is loaded and influence default queue timer selection and global client autoloading. No on-disk persistence.

Dependencies and integration: orchestrates `seq_clientmgr`, `seq_info`, `seq_system`, `seq_queue`, `seq_timer`, `seq_memory`, `seq_lock`, and sequencer-device autoload support.

Risks: init unwind must match successfully completed stages. Queue deletion happens after system client/proc removal on exit, so queued events must not call into removed clients. Timer defaults depend on Kconfig hrtimer setting.

Test signals: module load/unload, failure injection at each init stage, parameter parsing, dummy-client autoload default with module config, and device node alias creation.
