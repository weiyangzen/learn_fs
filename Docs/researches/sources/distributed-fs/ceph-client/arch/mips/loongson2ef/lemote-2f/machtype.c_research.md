<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c

Purpose: Infers Lemote 2F family machine type from PMON version when `machtype=` is absent.

Important APIs/types/functions: `mach_prom_init_machtype()` inspects `arcs_cmdline` for `PMON_VER=LM...`.

Control flow: LM8 maps to Yeeloong 8.9, LM6 to Fuloong 2F, LM9 to Lynloong, and other LM versions to NAS. It appends a `machtype=` argument with `get_system_type()`.

State and persistence: Mutates `mips_machtype` and appends to `arcs_cmdline`.

Dependencies and integration: Weak hook called by common machtype initialization.

Risks: `strcat()` assumes enough command-line buffer space. Version-prefix inference can misidentify future PMON strings.

Test signals: Old PMON boots without explicit `machtype=` should select the correct board and show the appended machtype in the command line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c -->
