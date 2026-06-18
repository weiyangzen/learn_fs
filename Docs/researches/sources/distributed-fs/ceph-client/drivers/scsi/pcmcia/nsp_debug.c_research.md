# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_debug.c

Purpose: optional debug helpers for `nsp_cs.c`, providing SCSI opcode/CDB, software phase, bus phase, and message-buffer dumps.

Important APIs/functions: `print_opcodek()`/`print_commandk()` decode CDBs; `show_command()` prints active commands; `show_phase()` maps command-private phase enum values; `show_busphase()` decodes hardware phase bits; `show_message()` dumps `MsgBuffer`.

Control flow/state: included only under `NSP_DEBUG`. Normal builds compile macros to no-ops. It stores only static string tables and reads current command/driver state.

Dependencies/integration: SCSI `COMMAND_SIZE()`, printk, `nsp_hw_data`, bus/phase constants, and command-private accessor support.

Risks/test signals: debug output can alter timing in PIO/IRQ paths, and phase-name arrays must stay synchronized with enums. Test debug build and expected command/phase/message logs.
