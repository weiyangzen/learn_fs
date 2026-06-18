# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_to_user.S

## Purpose

`copy_to_user.S` instantiates the Hexagon user-copy template for writes from kernel memory to userspace. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

It defines `FUNCNAME` as `raw_copy_to_user` and write-side exception fixup labels. Concrete declarations observed in the file: Includes: `copy_user_template.S`. Macros: `src_sav`, `dst_sav`, `src_dst_sav`, `d_dbuf`, `w_dbuf`, `dst`, `src`, `bytes`, `loopcount`, `FUNCNAME`.

## Control Flow, State, And Persistence

Runtime flow mirrors `copy_from_user` but faults are based on user destination writes; fixups compute remaining bytes.

## Dependencies And Integration Points

It integrates with `copy_user_template.S`, exception tables, and generic uaccess APIs.

## Risks And Test Signals

Risks are partial-copy accounting errors and unsafe writes after faults. Test signals are uaccess selftests, signal frame copyout, and invalid-pointer syscall tests.
 A local static signal for this file is that it has 80 lines and 1551 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
