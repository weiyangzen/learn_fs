## sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/vpe-mt.c` implements the MIPS MT VPE loader backend. It reserves VPE/TC resources, exposes a character device and sysfs attributes, starts and stops application/service processors on secondary VPEs, and exports module-facing VPE lifecycle helpers.

### Important APIs, Types, And Functions
Important globals are `major`, `hw_tcs`, and `hw_vpes`. Lifecycle functions are `vpe_run()`, `cleanup_tc()`, `vpe_alloc()`, `vpe_start()`, `vpe_stop()`, `vpe_free()`, `store_kill()`, `ntcs_show()`, `ntcs_store()`, `vpe_module_init()`, and `vpe_module_exit()`. Exported symbols are `vpe_alloc`, `vpe_start`, `vpe_stop`, and `vpe_free`. Sysfs attributes are `kill` and `ntcs`.

### Control Flow
Initialization checks MIPS MT capability and reserved VPE/TC limits, registers a character device and class device, disables MT/VPE execution, enters MVP configuration state, reads hardware TC/VPE counts, allocates TC/VPE descriptors for reserved TCs, halts and deactivates them, binds TCs to VPEs, copies config, and exits configuration state. `vpe_run()` verifies master VPE status, selects the first TC attached to the VPE, writes restart PC and context, marks the TC active, binds it to VPE1, configures XTC and VPE status/cause, enables the VPE, restores MT/VPE state, and sends start notifications. Stop/free/kill paths halt/deactivate TCs, release program memory, send stop notifications, and return descriptors to unused state.

### State, Persistence, And Dependencies
State spans VPE/TC descriptor lists from the VPE subsystem, VPE state fields, attached TC lists, `v->__start`, `v->ntcs`, loaded program memory, sysfs-visible device state, and CP0 MIPS MT registers. Dependencies include `asm/mipsmtregs.h`, `asm/mips_mt.h`, `asm/vpe.h`, `vpe_fops`, `get_vpe()`, `alloc_vpe()`, `alloc_tc()`, `release_vpe()`, `release_progmem()`, notifier lists, and kernel device/class/char APIs.

### Integration Points
This backend is used by the MIPS VPE loader character device and by kernel modules that allocate and control VPEs. It shares reserved TC/VPE policy with MT boot parameters such as `maxvpes` and `maxtcs`. It must coexist with SMP MT code, which may manage VPE enable state differently on SMP kernels.

### Risks
MT register programming must occur with interrupts and VPE/MT execution controlled or the system can hang. Resource cleanup on init failure is incomplete for some allocation points. Sysfs `kill` assumes a reserved VPE at `aprp_cpu_index()`. `vpe_stop()` and `vpe_free()` use list entry assumptions that require an attached TC. Notifier callbacks run during start/stop and can add side effects.

### Test Signals
Boot with and without MIPS MT, with `maxvpes` and `maxtcs` reserved, load a VPE program through the char device, start/stop/free it, write sysfs `ntcs` and `kill`, test init failure paths, and verify coexistence with SMP and VPE notifier clients.
