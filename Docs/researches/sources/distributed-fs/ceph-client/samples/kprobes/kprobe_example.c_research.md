# sources/distributed-fs/ceph-client/samples/kprobes/kprobe_example.c

Purpose: kprobe sample that instruments a configurable kernel symbol, defaulting to `kernel_clone`.

Important APIs/functions: `struct kprobe`, `register_kprobe`, `unregister_kprobe`, `pre_handler`, `post_handler`, `NOKPROBE_SYMBOL`, and arch-specific `pt_regs` field logging.

Control flow: init sets pre/post handlers and registers the probe. On hit, pre-handler logs symbol address and instruction pointer/status fields for the current architecture; post-handler logs flags/status. Exit unregisters.

State and persistence: global probe and module parameter `symbol`.

Dependencies and integration: kprobes, kallsyms, and architecture-specific register layouts.

Risks: probing hot or unsafe symbols can destabilize or flood logs. Handler code must be marked `NOKPROBE_SYMBOL` to avoid recursive probing.

Test signals: load with default or `symbol=<name>`, exercise the symbol, inspect logs, unload.
