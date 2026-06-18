# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/clocksource.h

Purpose: SPARC VDSO clocksource selector that advertises the architecture clock modes available to generic VDSO time code through `VDSO_ARCH_CLOCKMODES`, currently `VDSO_CLOCKMODE_NONE` and `VDSO_CLOCKMODE_ARCHTIMER`.

Important APIs/types/functions: macros/constants `__ASM_VDSO_CLOCKSOURCE_H`, `VDSO_ARCH_CLOCKMODES`.

Control flow: The file is declarative and is reached from generic VDSO clocksource/datapage code. There is no runtime branch in this header; the clock-mode list controls which VDSO counter paths can be selected by kernel VDSO data setup.

State and persistence behavior: It owns no mutable storage. Persistent state is the VDSO datapage clock-mode value written elsewhere; this header only constrains the valid architecture-specific values that user VDSO code may decode.

Dependencies and integration points: Includes/dependencies: none beyond VDSO clock-mode enum visibility from includers. Integration points include `vdso/datapage.h`, `vdso/gettimeofday.h`, and kernel VDSO clocksource setup.

Risks and test signals: Main risks are advertising a mode unsupported by `gettimeofday.h`, omitting a newly supported SPARC counter mode, or breaking generic VDSO builds through enum mismatch. Test signals include SPARC VDSO build coverage, clock_gettime fallback versus VDSO mode selection, and boot tests where the datapage selects `ARCHTIMER` or disables VDSO counter reads.
