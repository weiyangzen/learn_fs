# sources/distributed-fs/ceph-client/drivers/scsi/nsp32_debug.c

Purpose: optional debug code included by `nsp32.c` only when `NSP32_DEBUG` is defined. It decodes SCSI opcodes/CDBs, bus phases, AutoSCSI phase flags, and selected live ASIC registers for printk tracing.

Important APIs/functions: `print_opcodek()` maps opcode groups; `print_commandk()` prints command bytes and LBA/length for 6/10/12-byte CDBs; `show_command()`, `show_busphase()`, and `show_autophase()` are driver hooks; `nsp32_print_register()` dumps register state when `NSP32_SPECIAL_PRINT_REGISTER` is enabled.

Control flow/state: normal builds replace these hooks with no-ops. Debug builds call them from queueing and interrupt paths. The file has static string tables only; it observes command and hardware state through arguments and `nsp32_read*()` helpers.

Dependencies/integration: depends on SCSI command sizing, printk, bus-phase/AutoSCSI definitions from `nsp32.h`, and I/O helpers from `nsp32_io.h`. It is directly included, so all symbols are static.

Risks/test signals: debug printing and register reads can perturb timing-sensitive interrupt paths. Test with debug builds, expected CDB/phase output, and guarded register dumps only under the special mask.
