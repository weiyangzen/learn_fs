# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/os.S

Purpose: implements operating-system memory and exception call-outs shared by the 68060 FPSP and ISP packages. It provides data/instruction memory reads and writes for user or supervisor contexts, plus real trace/access exception exits.

Important APIs/types/functions: exported labels include `_060_dmem_write`, `_060_imem_read`, `_060_dmem_read`, `_060_dmem_read_byte`, `_060_dmem_read_word`, `_060_dmem_read_long`, `_060_imem_read_word`, `_060_imem_read_long`, `_060_dmem_write_byte`, `_060_dmem_write_word`, `_060_dmem_write_long`, `_060_real_trace`, and `_060_real_access`.

Control flow: generic read/write loops test bit 5 of the saved SR at `0x4(%a6)` to choose supervisor `move` instructions or user-space `movs` instructions. Known-size byte/word/long helpers clear success status in `%d1`, perform a single supervisor or user access, and return data in `%d0` for reads. Write helpers similarly store from `%d0`. `_060_real_trace` branches to `trap`; `_060_real_access` branches to `buserr`. Exception-table entries map faults in user `movs` access labels to a `.fixup` routine that returns `%d1 = -1`.

State and persistence: no persistence. Runtime state is limited to copied bytes/words/longs, `%d1` status, and exception-table recovery for access faults.

Dependencies/integration: used by call-out tables in `fskeleton.S` and `iskeleton.S`. Depends on Linux/m68k exception table and `.fixup` mechanisms, `trap`, `buserr`, and 68060 `movs` address-space instructions.

Risks: generic byte loops decrement `%d0` before `dbra`; zero-length calls would underflow and copy too much, so callers must pass positive byte counts. Known-size helpers rely on exception table coverage for every user-access label. Supervisor-mode paths do raw kernel memory moves and will not recover through user access fixups.

Test signals: user and supervisor reads/writes for byte/word/long and arbitrary byte counts, invalid user addresses returning `%d1=-1`, instruction vs data read call-outs, trace and access exception exits, and integration with FPSP/ISP package memory callbacks.
