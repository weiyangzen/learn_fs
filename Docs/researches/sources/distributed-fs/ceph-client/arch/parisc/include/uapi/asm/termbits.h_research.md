<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h

Source read size: 149 lines, 3628 bytes.

Purpose: defines PA-RISC termios structures, control-character indexes, line discipline flags, baud rates, and tcsetattr action values. Important APIs/types: `tcflag_t`, `NCCS`, `struct termios`, `struct termios2`, `struct ktermios`, `VINTR` through `VEOL2`, `IUCLC`/`IXON`/`IXOFF`, output delay masks, `CBAUD`, `BOTHER`, extended baud constants, local flags, and termios action constants. Control flow: tty ioctl handlers copy these structures and update terminal state. State and persistence: termios settings persist per tty until changed. Dependencies and integration points: `ioctls.h`, tty core, serial drivers, libc `termios`, shells and terminal tools. Risks: `NCCS` and numeric flags are ABI-specific; wrong baud or c_cc indexes break terminal behavior. Test signals: `stty`, pty/tty selftests, serial baud tests, canonical/raw mode tests, and compat ioctl layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/termbits.h -->
