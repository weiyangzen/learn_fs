# File Research: sources/cow-pools/bcachefs-tools/linux/percpu_register.c

Constructor glue registering bcachefs lock-graph percpu init/exit callbacks with the userspace percpu registry. This ensures `bch2_lock_graph` is initialized for existing and future per-thread percpu chunks.
