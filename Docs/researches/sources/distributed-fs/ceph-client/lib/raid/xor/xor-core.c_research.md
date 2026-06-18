# sources/distributed-fs/ceph-client/lib/raid/xor/xor-core.c

Purpose: central dispatcher and selector for RAID5-style XOR parity functions.

Important APIs and flow: exported `xor_gen()` validates task context, nonzero 512-byte-multiple length, then invokes the selected function through `static_call(xor_gen_impl)`. `xor_register()` adds templates to an init-time list; `xor_force()` sets a forced template. `calibrate_xor_blocks()` allocates benchmark pages, times each registered template over `BENCH_SIZE` and `REPS`, records `speed`, and updates the static call to the fastest. `xor_init()` invokes `arch_xor_init()`, handles forced selection, and chooses either early default or module-time calibration.

State and persistence: global static call target is runtime process state. `template_list` is init data, `forced_template` may persist after init, and template speed fields are filled by calibration.

Dependencies and integration: depends on module/init APIs, jiffies/ktime/preemption, static calls, and architecture `xor_arch.h` when configured. Consumers call `linux/raid/xor.h`.

Risks and test signals: wrong dispatch affects RAID5 parity globally. Risks include empty template list, calibration timing instability, and context restrictions. Signals include boot logs, KUnit `xor` suite, and module/built-in init ordering tests.
