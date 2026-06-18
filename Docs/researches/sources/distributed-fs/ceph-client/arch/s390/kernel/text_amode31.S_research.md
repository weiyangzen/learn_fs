## sources/distributed-fs/ceph-client/arch/s390/kernel/text_amode31.S

Purpose: Provides assembly routines that must execute below 2 GB in 31-bit addressing mode, mainly DIAG helpers and a reset path used by firmware/hypervisor interfaces.

Important symbols: `_diag14_amode31`, `_diag210_amode31`, `_diag8c_amode31`, `_diag26c_amode31`, `_diag0c_amode31`, `_diag308_reset_amode31`, local low-memory state such as `ctlregs`, `fpctl`, `prefix`, `continue_psw`, and `restart_diag308_psw`.

Control flow: Each helper switches from 64-bit to 31-bit mode with `sam31`, issues the relevant DIAG instruction, captures condition code or fallback errno, switches back with `sam64`, and returns through a local expoline-style branch macro. The DIAG 308 reset path saves control registers, FPC, prefix, and PSW, clears lowcore protection, installs a restart PSW at absolute zero, performs reset, switches architecture/mode back, restores state, and returns.

State and persistence: Uses `.amode31.data` scratch storage below 2 GB and temporarily changes addressing mode, prefix register, control registers, and PSW state. Exception-table entries recover faults back into 64-bit mode with error returns.

Dependencies and integration: Relies on linker placement of `.amode31.*` in `vmlinux.lds.S`, s390 DIAG/SIGP semantics, exception-table macros, and callers in diag/IPL/dump paths that require low-address callable code.

Risks and test signals: Risks are failure to restore machine state, exception handling while in 31-bit mode, and linker placement above 2 GB. Test signals are DIAG helper return codes, dump/reset flows, exception-table recovery, and linker symbols `_samode31`/`_eamode31` in vmcore info.
