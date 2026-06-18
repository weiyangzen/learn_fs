## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpuidle.h

Purpose: declares PowerNV idle-state metadata and bit layouts for POWER stop/nap/sleep/winkle management.

Important APIs/types/functions: defines thread states (`PNV_THREAD_RUNNING`, `NAP`, `SLEEP`, `WINKLE`), packed core-idle lock/count/thread bits, PSSCR default value/mask macros, `struct pnv_idle_states_t`, `pnv_idle_states`, `nr_pnv_idle_states`, `pnv_cpu_offline()`, `validate_psscr_val_mask()`, and `report_invalid_psscr_val()`.

Control flow: runtime code validates firmware-provided PSSCR values, reports ESL/EC mismatches, and tracks per-thread core idle transitions with lock and winkle bitfields. Offline paths call `pnv_cpu_offline()`.

State and persistence: global idle-state arrays and core idle bitfields track CPU/core low-power state. PSSCR values persist as firmware-derived configuration used during idle entry.

Dependencies and integration: only active for `CONFIG_PPC_POWERNV`; depends on PSSCR bit definitions from processor headers and integrates with `kernel/idle_book3s.S`, cpuidle drivers, CPU offline, and firmware device-tree idle descriptions.

Risks and test signals: incorrect bitfield layout or PSSCR defaults can lose CPU state, wake at the wrong vector, or hang offline. Test signals include PowerNV cpuidle state enumeration, stop-state validation logs, CPU offline/online stress, suspend-like idle loops, and firmware variants with legacy RL-only PSSCR data.
