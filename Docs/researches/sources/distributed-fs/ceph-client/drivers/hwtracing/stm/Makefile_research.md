
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/Makefile

Purpose: kbuild rules for STM core, protocols, dummy driver, and source modules.

Important APIs/types/functions: builds `stm_core` from `core.o policy.o`; maps protocol objects to `stm_p_basic.o` and `stm_p_sys-t.o`; maps optional drivers to `dummy_stm.o`, `stm_console.o`, `stm_heartbeat.o`, and `stm_ftrace.o`.

Control flow: kbuild uses enabled Kconfig symbols to decide which composite objects/modules to build.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with Kconfig symbol names and source filenames.

Risks: object renames or missing composite rules break module names used by autoload, especially `request_module_nowait("stm_p_basic")` in core.

Test signals: build each symbol as module and built-in; verify resulting module names match runtime request strings.
