# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/powersave.S

Purpose: low-level PA6T idle entry routines for spin/doze power-saving modes.

Important APIs and control flow: `idle_spin` simply returns. `idle_doze` loads `_doze` and branches to `sleep_common`. `sleep_common` saves LR/stack, optionally checks cpufreq astate and skips power saving unless astate is zero, disables DR/IR/ME/EE bits from MSR, calls the selected sleep opcode routine, restores MSR and stack state, and returns. `_doze` executes a pre-sleep sync/ptesync sequence and the raw DOZE opcode, then branches to itself if execution continues unexpectedly.

State, dependencies, and risks: state is CPU MSR, stack frame, and optional cpufreq astate. Dependencies include PA6T sleep opcodes, `check_astate`, exception wake handling in `idle.c`, and PowerPC assembly ABI. Risks include running with translation/interrupt bits disabled, wake path relying on system-reset exception repair, and raw opcodes for assembler compatibility. Test signals are idle entry/exit under timer and external interrupts, astate gating, and no stack/MSR corruption after wake.
