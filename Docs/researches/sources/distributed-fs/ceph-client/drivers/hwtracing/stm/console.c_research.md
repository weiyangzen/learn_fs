
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/console.c

Purpose: STM source module that forwards kernel console messages to a linked STM device.

Important APIs/types/functions: static `stm_console` embeds `stm_source_data` and `struct console`. `stm_console_write()` calls `stm_source_write()`. Link/unlink callbacks register and unregister the console. Module init/exit register/unregister the STM source device.

Control flow: when users link the `console` STM source to an STM device through sysfs, the source link callback registers a console named `stm_console` with `CON_PRINTBUFFER`; console writes then flow to STM channel 0. Unlink removes the console.

State and persistence: one static source/console object; console registration exists only while linked.

Dependencies and integration: depends on generic STM source APIs and Linux console subsystem. Requires an STM policy and source link before output works.

Risks: registering with `CON_PRINTBUFFER` can emit backlog on link. Console context constraints mean `stm_source_write()` must remain low-overhead and safe for console write paths.

Test signals: register module, link source to STM, confirm kernel messages appear in trace, unlink and verify console removed, test relink without duplicate console registration.
