# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_from_user.S

## Purpose

`copy_from_user.S` instantiates the Hexagon user-copy template for reads from userspace into kernel memory. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines `FUNCNAME` as `raw_copy_from_user` and supplies exception labels that return the uncopied byte count. Concrete declarations observed in the file: Includes: `copy_user_template.S`. Macros: `src_sav`, `dst_sav`, `src_dst_sav`, `d_dbuf`, `w_dbuf`, `dst`, `src`, `bytes`, `loopcount`, `FUNCNAME`.

## Control Flow, State, And Persistence

Runtime flow copies 8/4/2/1-byte chunks using the shared template; exception fixups adjust `r2` for remaining bytes.

## Dependencies And Integration Points

It integrates with `copy_user_template.S`, exception tables, uaccess core, and exported user-copy symbols.

## Risks And Test Signals

Risks are bad residual counts, missing exception entries, and kernel faults on invalid userspace pointers. Test signals are uaccess selftests, `copy_from_user` fault injection, and syscall argument copying.
 A local static signal for this file is that it has 102 lines and 1687 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
