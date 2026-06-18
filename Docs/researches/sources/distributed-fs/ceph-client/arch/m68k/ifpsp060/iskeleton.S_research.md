# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/iskeleton.S

Purpose: adapts the Motorola 68060 Integer Software Package to Linux/m68k. It defines OS call-outs, entry stubs for unimplemented integer/CAS emulation, the ISP call-out table, and includes `isp.sa`.

Important APIs/types/functions: exported labels include `_060_isp_done`, `_060_real_chk`, `_060_real_divbyzero`, `_060_real_cas`, `_060_real_cas2`, `_060_real_lock_page`, `_060_real_unlock_page`, `_060_isp_unimp`, `_060_isp_cas`, `_060_isp_cas2`, `_060_isp_cas_finish`, `_060_isp_cas2_finish`, `_060_isp_cas_inrange`, `_060_isp_cas_terminate`, and `_060_isp_cas_restart`.

Control flow: `_060_isp_done` returns directly with `rte` for supervisor-mode frames, but for user-mode frames it saves an interrupt frame, gets current task, and jumps to `ret_from_exception` so Linux can deliver signals/reschedule. CHK and divide-by-zero exits branch to `trap`. CAS/CAS2 call-outs re-enter the package through offsets. `_060_real_lock_page` sets SFC/DFC based on user/supervisor mode, uses 68060 `plpaw` to prefetch/lock one or two pages, records access failures through exception-table fixups, restores function codes, and returns a fault-status long in `%d0`. `_060_real_unlock_page` currently returns success without action.

State and persistence: no persistent state. Runtime state includes exception stack frames, SFC/DFC control registers, prefetch/fault status in `%d0`, and the static `_I_CALL_TOP` table.

Dependencies/integration: includes Linux m68k entry macros and asm offsets, references `trap`, `ret_from_exception`, `_060_real_trace`, `_060_real_access`, and memory call-outs from `os.S`. Includes `isp.sa` at the end.

Risks: user/supervisor return split in `_060_isp_done` is critical for signal and reschedule handling. `plpaw` fixups must return correctly encoded FSLW values or package access-error synthesis fails. The call-out table has the same fixed 128-byte ABI risk as the FPSP wrapper.

Test signals: unimplemented integer emulation returning to user and supervisor contexts, CHK/divide-by-zero trap paths, CAS/CAS2 emulation, page-lock success and fault fixups for word/long operands crossing pages, SFC/DFC restoration, and call-out table size/order validation.
