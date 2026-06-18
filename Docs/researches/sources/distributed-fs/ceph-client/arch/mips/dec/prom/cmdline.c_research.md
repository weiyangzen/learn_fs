# sources/distributed-fs/ceph-client/arch/mips/dec/prom/cmdline.c

Purpose: imports the DEC PROM command line into `arcs_cmdline`.

Important API: `prom_init_cmdline(s32 argc, s32 *argv, u32 magic)` chooses the first argument index based on PROM type: non-REX starts at argument 1, REX starts at argument 2.

Control flow and state: appends each argument separated by spaces using `strcat()`. The resulting command line persists globally for normal boot parsing.

Dependencies and risks: depends on PROM argument pointer validity and `prom_is_rex()`. There is no explicit bounds checking here, so very long PROM argument strings would risk overflowing `arcs_cmdline` if not constrained elsewhere.

Test signals: boot with PROM arguments on REX and non-REX systems and verify `/proc/cmdline`.
