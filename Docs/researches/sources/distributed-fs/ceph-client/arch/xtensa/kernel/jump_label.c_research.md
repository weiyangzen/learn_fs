<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c

Purpose: implements Xtensa static key/jump label patching. Important functions are `arch_jump_label_transform`, `patch_text`, `patch_text_stop_machine`, and `local_patch_text`; constants encode endian-specific jump and NOP instructions.

Control flow computes relative jump displacement, verifies it fits the 128 KiB Xtensa jump range, encodes either a J instruction or NOP, and patches text. SMP uses `stop_machine_cpuslocked`; the last arriving CPU patches and flushes local icache while other CPUs wait and invalidate their icaches. UP disables local interrupts around the patch. Persistent state is executable kernel text and per-patch atomic synchronization. Dependencies include `linux/jump_label.h`, stop_machine, cacheflush, CPU hotplug locking, and endianness. Integration points are static branches, tracepoints, scheduler/static key users, and text patching. Risks are out-of-range jumps, endian encoding errors, icache coherency, and patching while CPUs execute target text. Test signals include jump label selftests, static branch toggling under SMP load, ftrace/static key users, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/jump_label.c -->
