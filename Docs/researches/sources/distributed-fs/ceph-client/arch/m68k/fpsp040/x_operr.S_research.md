# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_operr.S

Purpose: implements `fpsp_operr`, the operand-error FPSP handler. It corrects 68040 move-out integer conversion behavior, stores the 68881-compatible result when required, posts operand-error/inexact state, or forwards enabled traps to kernel handlers.

Important APIs/types/functions: exported label is `fpsp_operr`. Internal helpers include `operr_long`, `operr_word`, `operr_byte`, `operr_nan`, `store_max`, `operr_store`, `dest_mem`, `check_upper`, `end_operr`, `ck_inex`, and `take_inex`. External dependencies are `mem_write`, `real_operr`, `real_inex`, `get_fline`, `fpsp_done`, and `reg_dest`.

Control flow: the handler saves local state and only performs special correction for TFLAG/opclass-3 move-out operations with byte/word/long destinations. It distinguishes NaN conversions from integer overflow and from the 040's incorrectly signaled largest-negative-integer cases. Corrected or saturated values are written through `operr_store`, which chooses data register or memory by reading the original F-line. Enabled operand-error traps branch to `real_operr`; disabled traps may still chain to `real_inex` if inexact is enabled and reported; otherwise they finish through `fpsp_done`.

State and persistence: no persistence. It mutates `USER_FPSR`, clears incorrect inexact bits for saturated integer overflow, may write user memory/register destinations, and may rewrite `EXC_VEC` for inexact chaining.

Dependencies/integration: relies on `fpsp.h` frame fields `FPTEMP`, `ETEMP`, `STAG`, `CMDREG1B`, `EXC_EA`, and FPSR/FPCR bit definitions. Uses shared `reg_dest` and `mem_write` destination paths, and kernel exception entries for real traps.

Risks: integer conversion edge cases are dense and hardware-specific. The code intentionally writes "garbage-compatible" NaN-derived upper mantissa bits for some disabled cases; simplifying it could break compatibility. `operr_store` depends on correct F-line mode bits and `EXC_EA` validity.

Test signals: byte/word/long move-out NaN conversion, positive/negative integer overflow saturation, largest negative byte/word/long false-operr correction, destination Dn vs memory, enabled vs disabled operand-error traps, combined inexact handling, and FPSR bit cleanup.
