
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes_head.S

Purpose: executable slot reservation and detour-buffer template used by `optprobes.c` to build optimized kprobe trampolines close enough to kernel text for relative branches.

Important APIs/types/functions: exported `optinsn_slot`; `optprobe_template_entry`; `optprobe_template_op_address`; `optprobe_template_call_handler`; `optprobe_template_insn`; `optprobe_template_call_emulate`; `optprobe_template_ret`; `optprobe_template_end`; `SAVE_30GPRS/REST_30GPRS`; `TEMPLATE_FOR_IMM_LOAD_INSNS`.

Control flow: the file reserves a 64 KiB aligned text area for detour slots. The template allocates an interrupt-frame-sized `pt_regs` image on the stack, saves GPRs and SPR-derived state, records trap/MSR/CTR/LR/XER/CR and PPC64 soft-mask state, loads kernel TOC on PPC64, loads a patched `optimized_kprobe` pointer into r3, passes the `pt_regs` pointer in r4 to `optimized_callback`, then calls `emulate_step` with the same regs and a patched original instruction. It restores saved state, releases the stack frame, and executes a patched return branch.

State and persistence: `optinsn_slot` is static executable storage; copied templates contain patched immediates and branches. Runtime stack state is temporary per probe hit.

Dependencies and integration: depends on pt_regs offsets from `asm-offsets.h`, PowerPC calling convention, PPC32/PPC64 save/restore differences, PACA TOC loading, and C-side template index calculations.

Risks: stack frame layout must exactly match `struct pt_regs`; failing to restore MSR/CR/LR/CTR/XER/GPRs corrupts interrupted code; template size/index changes must stay synchronized with `optprobes.c`; slot locality is required for relative branch reach.

Test signals: disassemble generated detour buffers, run optimized probes on PPC32/PPC64, verify register preservation with stress probes, and confirm template index constants match labels.
