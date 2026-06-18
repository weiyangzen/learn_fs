# sources/distributed-fs/ceph-client/arch/x86/boot/regs.c

Purpose: initializes BIOS register blocks before interrupt calls.

Important APIs and state: exports `initregs(struct biosregs *reg)`.

Control flow: zeroes the register block, sets carry flag in `eflags` as a defensive default, and initializes `ds`, `es`, `fs`, and `gs` from current segment helper functions.

Dependencies and integration: used by nearly every BIOS-interrupt caller in setup code, including memory, keyboard, video, EDD, and tty.

Risks and test signals: default CF helps detect BIOS helper paths that fail to clear status. Segment initialization must match the setup environment. Test by exercising BIOS calls and verifying callers handle CF correctly.
