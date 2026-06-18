## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore-asm.S

### Purpose
`subcore-asm.S` provides the secondary-thread real-mode helper used while splitting a POWER8 core into subcores.

### Important APIs, Types, And Functions
The exported assembly symbol is `split_core_secondary_loop(u8 *state)`. It uses sync step constants from `subcore.h` and SPRs such as HID0, LDBAR, PMMAR, PMCR, RPR, SDR1, LPID, PCR, and HDEC.

### Control Flow
The routine saves MSR, disables interrupts, transitions to real mode via SRR0/SRR1 and `rfid`, reads unsplit SPR values, stores `SYNC_STEP_REAL_MODE` to the shared state byte, spins until HID0 reports 2-way or 4-way LPAR mode, initializes per-subcore SPRs, restores saved SPR values including SDR1, and returns to virtual mode with the original MSR.

### State, Persistence, And Dependencies
State is the caller-provided byte used for synchronization and CPU SPR state preserved across the split. It depends on exact POWER8 HID0 semantics and the C side's stop-machine synchronization.

### Integration Points
`subcore.c` calls this helper from nonzero threads during `split_core()`.

### Risks
Interrupts must stay disabled so SRR0/SRR1 are not clobbered. Returning to virtual mode before SDR1 is restored would be unsafe. HID0 bit definitions and SPR save/restore order are architecture-sensitive.

### Test Signals
Successful 1-to-2 and 1-to-4 subcore transitions, no hangs in the real-mode wait loop, preserved MMU operation after split, and offline-thread participation are key signals.
