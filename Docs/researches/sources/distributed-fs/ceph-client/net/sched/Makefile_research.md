# sources/distributed-fs/ceph-client/net/sched/Makefile

Purpose: maps traffic-control Kconfig symbols to the scheduler, classifier, ematch, and action object files compiled for `net/sched`.

Important build mappings: unconditional core objects are `sch_generic.o` and `sch_mq.o`; `CONFIG_NET_SCHED` adds `sch_api.o` and `sch_blackhole.o`; `CONFIG_NET_CLS_ACT` adds `act_api.o`. The listed action files map directly from action configs, including `act_gact.o`, `act_bpf.o`, `act_connmark.o`, `act_csum.o`, `act_ct.o`, `act_ctinfo.o`, `act_gate.o`, and `act_ife.o`. IFE metadata plugins map to `act_meta_mark.o`, `act_meta_skbprio.o`, and `act_meta_skbtcindex.o`.

Control flow: kbuild evaluates `obj-$(CONFIG_...) += file.o` lines. Built-in `y` symbols link into the kernel or parent object; module `m` symbols become loadable modules with names implied by the object basename.

State and persistence: no runtime state. The file persists the source-to-object build contract used by kernel builds and module packaging.

Dependencies and integration: must remain consistent with `Kconfig`, source file module aliases, and any helper objects such as `sch_mqprio_lib.o`. It also includes classifier and ematch object lists, so it is the build join point for much of `net/sched`.

Risks: missing or misspelled object mappings create configured-but-unbuilt features. Objects added without matching Kconfig can be unexpectedly built or never built. Module names in Kconfig help should track these object names.

Test signals: per-symbol module builds, `make M=net/sched`, randconfig coverage, and checking that `modprobe act_*`, `sch_*`, `cls_*`, and `em_*` aliases match selected config outputs.
