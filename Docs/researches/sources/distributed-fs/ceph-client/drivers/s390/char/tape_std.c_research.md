# sources/distributed-fs/ceph-client/drivers/s390/char/tape_std.c

Purpose: implements common IBM tape CCW command builders and MTIO operation handlers shared by tape disciplines.

Important APIs/types/functions: exports `tape_std_assign`, `tape_std_unassign`, `tape_std_read_block_id`, `tape_std_terminate_write`, MT operations for load, set block, reset, forward/backward spacing, write EOF, rewind/offline/unload, EOM, retension, erase, compression, `tape_std_read_block`, `tape_std_write_block`, and `tape_std_process_eov`.

Control flow: functions allocate `tape_request`s, fill CCW chains using helpers from `tape.h`, execute through `tape_do_io*`, then free requests. Repeated spacing/write-mark operations build repeated CCWs. `tape_std_terminate_write` writes pending tapemarks then backs over one. Assign uses an interruptible request with a 2-second timer that cancels stuck assignments. Read/write block builders map IDAL buffer arrays into chained READ_FORWARD/WRITE CCWs.

State and persistence: updates per-device mode-set byte, fixed block size, and `required_tapemarks`. No persistent state beyond the tape medium effects of commands such as write marks, erase, rewind, unload, and EOV handling.

Dependencies and integration: depends on tape core request execution, IDAL buffer arrays, `tape_std.h` command constants, mtio operation numbers, and discipline command tables such as 3490's `mtop_array`.

Risks: large `mt_count` can allocate large CCW arrays unless upper layers chunk selected operations; assignment timeout races with normal completion; retension intentionally ignores the first command return; EOM scanning depends on FSR returning positive over tapemarks; compression mutates mode-set byte before executing.

Test signals: MTIO command coverage, fixed/variable block read/write builders, assignment busy timeout, EOV write behavior, set-block validation against `MAX_BLOCKSIZE`, and residual-count behavior for FSR/BSR over tapemarks.
